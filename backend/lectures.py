"""Additive local-only lecture packs. This module never executes C++ or edits lecture one."""
import hashlib
import io
import json
import re
import zipfile
from .catalog import ROOT,DAY_NAMES,catalog,get_task,public_task,student_files
from . import storage

SOURCE=ROOT/'content/lectures-02-03'

def available():
    return sorted(int(path.parent.name.removeprefix('lecture-')) for path in (ROOT/'days').glob('day-*/lectures/lecture-*/manifest.json'))

def source_folder(data):
    return ROOT/data.get('sourceRoot','content/lectures-02-03')/f'lecture-{data["number"]:02}'

def manifest(number):
    paths=list((ROOT/'days').glob(f'day-{number:02}-*/lectures/lecture-{number:02}/manifest.json'))
    if len(paths)!=1:raise ValueError('Лекция не найдена')
    path=paths[0]
    return json.loads(path.read_text(encoding='utf-8'))

def reading(number=None):
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS lecture_pack_reading (lecture INTEGER, section TEXT, completed INTEGER NOT NULL, PRIMARY KEY(lecture,section))')
        rows=db.execute('SELECT lecture,section FROM lecture_pack_reading WHERE completed=1 ORDER BY lecture,section').fetchall()
    return [section for lecture,section in rows if lecture==number] if number else [f'lecture-{lecture}/{section}' for lecture,section in rows]

def mark_read(number,section,completed):
    manifest(number)
    if section not in {f'chapter-{i}' for i in range(1,5)} or type(completed) is not bool:raise ValueError('Укажите главу 1–4 и отметку прочтения')
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS lecture_pack_reading (lecture INTEGER, section TEXT, completed INTEGER NOT NULL, PRIMARY KEY(lecture,section))')
        db.execute('INSERT INTO lecture_pack_reading VALUES(?,?,?) ON CONFLICT(lecture,section) DO UPDATE SET completed=excluded.completed',(number,section,int(completed)))
    return reading(number)

def lecture(number):
    data=manifest(number);source=source_folder(data);raw=(source/data['sourceFilename']).read_bytes();text=raw.decode('utf-8')
    summary=re.escape(data['summaryHeading']) if data.get('summaryHeading') else r'Выводы из лекции.+|Заключение и маршрут к лабораторной'
    points=list(re.finditer(r'^# (?:Глава [1-4]\..+|'+summary+r')\r?$',text,re.M))
    if len(points)!=5:raise ValueError('Ожидаются четыре главы и итоги')
    sections=[dict(id='overview',title='Обзор и маршрут',markdown=text[:points[0].start()])]
    for i,match in enumerate(points):
        section=dict(id=f'chapter-{i+1}' if i<4 else 'summary',title=match[0][2:].strip(),markdown=text[match.start():points[i+1].start() if i+1<len(points) else len(text)])
        if i<4:section.update(chapter=i+1,checkId=data['checkIds'][i])
        sections.append(section)
    if data.get('localInstructionsFilename'):
        local=(source/data['localInstructionsFilename']).read_bytes().decode('utf-8')
    else:
        instructions=(source/'CODEX_INSTRUCTIONS.md').read_bytes().decode('utf-8')
        start='## Компиляция только на компьютере ученика' if number==2 else '## Компиляция только локально'
        local=start+instructions.split(start,1)[1].split('\n## ',1)[0]
    return {**data,'sections':sections,'checks':[public_task(get_task(key)) for key in data['checkIds']],'projects':[public_task(get_task(key)) for key in data['projectIds']],'reading':reading(number),'localInstructions':local,'sourceSha256':hashlib.sha256(raw).hexdigest()}

def overview():
    result=[]
    for number in available():
        data=lecture(number)
        result.append({k:data[k] for k in ('number','title','attribution','checkIds','projectIds')}|{'chapters':[dict(id=s['id'],title=s['title'],chapter=s['chapter']) for s in data['sections'] if 'chapter' in s]})
    return result

def main_bytes(number,filename):
    data=manifest(number)
    names={main['filename'] for key in data['checkIds']+data['projectIds'] for main in get_task(key)['localMains']}
    if filename not in names:raise ValueError('Проверочный файл не найден')
    return (source_folder(data)/filename).read_bytes()

def guide(task):
    stages=[]
    for item in task.get('localMains',[]):
        stages.append({**item,'source':main_bytes(task['packLecture'],item['filename']).decode('utf-8'),'title':'Постфиксный вычислитель' if 'POSTFIX' in item['filename'] else 'Базовая локальная проверка'})
    if not stages:stages=[dict(id='reflection',title='Код и письменное объяснение',filename='',source='',expectedOutput='')]
    prior=next((a for a in storage.history(task['id']) if a['mode']=='self-check'),{})
    return dict(task=task['id'],stages=stages,reports=prior.get('stageReports',{}),requirements=task['reviewRequirements'],history=storage.history(task['id']))

def report(task,body,files):
    current=guide(task);stage=body.get('stage');status=body.get('status')
    statuses=('SELF_CHECKED','NEEDS_WORK','REPEAT_REQUESTED','IN_PROGRESS') if task.get('packLecture')==4 else ('SELF_CHECKED','NEEDS_WORK','REPEAT_REQUESTED')
    if stage not in {s['id'] for s in current['stages']} or status not in statuses:raise ValueError('Укажите этап и результат самостоятельной проверки')
    confirmed=body.get('confirmed',[])
    if not isinstance(confirmed,list) or any(type(i) is not int or i<0 or i>=len(current['requirements']) for i in confirmed):raise ValueError('Неизвестный критерий проверки')
    if status=='SELF_CHECKED' and set(confirmed)!=set(range(len(current['requirements']))):raise ValueError('Проверьте все критерии перед положительной отметкой')
    details={key:body.get(key,'') for key in ('errorNotes','explanation','hints')}
    if task.get('packLecture')==4:
        details.update({key:body.get(key,'') for key in ('compileNotes','reviewNotes','complexityNotes')})
    if any(not isinstance(value,str) or len(value)>8000 for value in details.values()):raise ValueError('Текст отметки должен содержать не более 8000 символов')
    memory=body.get('memory','not_checked')
    if memory not in ('not_checked','reviewed','errors','not_required') and not (task.get('packLecture')==4 and memory=='sanitized'):raise ValueError('Неизвестная отметка проверки памяти')
    if status=='SELF_CHECKED' and memory=='errors':raise ValueError('Сначала исправьте отмеченные ошибки памяти')
    if task['section']=='lecture-theory' and status=='SELF_CHECKED' and not details['explanation'].strip():raise ValueError('Добавьте своё объяснение: оно является частью закрепления')
    extra={}
    if task.get('trackImplementation'):
        steps=body.get('implementation',[])
        if not isinstance(steps,list) or any(type(i) is not int or i<0 or i>=len(task['projectSteps']) for i in steps):raise ValueError('Неизвестный этап реализации')
        if status=='SELF_CHECKED' and set(steps)!=set(range(len(task['projectSteps']))):raise ValueError('Завершите все этапы реализации перед итоговой отметкой')
        extra['implementation']=steps
    if task.get('requiresComplexity') and status=='SELF_CHECKED' and not details['complexityNotes'].strip():raise ValueError('Обоснуйте сложность своей реализации')
    reports={**current['reports'],stage:dict(status=status,confirmed=confirmed,memory=memory,**details,**extra)}
    states=[reports.get(s['id'],{}).get('status') for s in current['stages']]
    overall='SELF_CHECKED' if all(s=='SELF_CHECKED' for s in states) else 'NEEDS_WORK' if 'NEEDS_WORK' in states else 'REPEAT_REQUESTED' if 'REPEAT_REQUESTED' in states else 'IN_PROGRESS'
    return dict(status=overall,mode='self-check',score=100 if overall=='SELF_CHECKED' else 0,manual=True,stageReports=reports,codeHash=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),message='Ваша отметка сохранена. Сайт не выполнял C++ и не подтверждает автоматическое прохождение тестов.')

def bundle(task):
    current=guide(task);files=student_files(task);content={name:value for name,value in files.items()}
    for stage in current['stages']:
        if stage['filename']:
            content[stage['filename']]=stage['source'];content[stage['filename']+'.expected.txt']=stage['expectedOutput']
    content['README.md']=task['prompt']+'\n\n'+lecture(task['packLecture'])['localInstructions']+'\n\nСобирайте каждый MAIN отдельно: в каждом определена своя функция main. Это ваши файлы и авторские проверки, без готовых реализаций.\n'
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,value in content.items():archive.writestr(name,value)
    return output.getvalue()
