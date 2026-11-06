"""Additive local-only lecture packs. This module never executes C++ or edits lecture one."""
import hashlib
import io
import json
import re
import zipfile
from .catalog import ROOT,DAY_NAMES,catalog,get_task,public_task,student_files
from . import storage

SOURCE=ROOT/'content/lectures-02-03'

def manifest(number):
    if number not in (2,3):raise ValueError('Лекция не найдена')
    path=ROOT/'days'/f'day-{number:02}-{DAY_NAMES[number-1]}'/'lectures'/f'lecture-{number:02}'/'manifest.json'
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
    data=manifest(number);raw=(SOURCE/f'lecture-{number:02}'/data['sourceFilename']).read_bytes();text=raw.decode('utf-8')
    points=list(re.finditer(r'^# (?:Глава [1-4]\..+|Выводы из лекции.+|Заключение и маршрут к лабораторной)\r?$',text,re.M))
    if len(points)!=5:raise ValueError('Ожидаются четыре главы и итоги')
    sections=[dict(id='overview',title='Обзор и маршрут',markdown=text[:points[0].start()])]
    for i,match in enumerate(points):
        section=dict(id=f'chapter-{i+1}' if i<4 else 'summary',title=match[0][2:].strip(),markdown=text[match.start():points[i+1].start() if i+1<len(points) else len(text)])
        if i<4:section.update(chapter=i+1,checkId=data['checkIds'][i])
        sections.append(section)
    instructions=(SOURCE/f'lecture-{number:02}'/'CODEX_INSTRUCTIONS.md').read_bytes().decode('utf-8')
    start='## Компиляция только на компьютере ученика' if number==2 else '## Компиляция только локально'
    local=instructions.split(start,1)[1].split('\n## ',1)[0]
    return {**data,'sections':sections,'checks':[public_task(get_task(key)) for key in data['checkIds']],'projects':[public_task(get_task(key)) for key in data['projectIds']],'reading':reading(number),'localInstructions':start+local,'sourceSha256':hashlib.sha256(raw).hexdigest()}

def overview():
    result=[]
    for number in (2,3):
        data=lecture(number)
        result.append({k:data[k] for k in ('number','title','attribution','checkIds','projectIds')}|{'chapters':[dict(id=s['id'],title=s['title'],chapter=s['chapter']) for s in data['sections'] if 'chapter' in s]})
    return result

def main_bytes(number,filename):
    data=manifest(number)
    names={main['filename'] for key in data['checkIds']+data['projectIds'] for main in get_task(key)['localMains']}
    if filename not in names:raise ValueError('Проверочный файл не найден')
    return (SOURCE/f'lecture-{number:02}'/filename).read_bytes()

def guide(task):
    stages=[]
    for item in task.get('localMains',[]):
        stages.append({**item,'source':main_bytes(task['packLecture'],item['filename']).decode('utf-8'),'title':'Постфиксный вычислитель' if 'POSTFIX' in item['filename'] else 'Базовая локальная проверка'})
    if not stages:stages=[dict(id='reflection',title='Код и письменное объяснение',filename='',source='',expectedOutput='')]
    prior=next((a for a in storage.history(task['id']) if a['mode']=='self-check'),{})
    return dict(task=task['id'],stages=stages,reports=prior.get('stageReports',{}),requirements=task['reviewRequirements'],history=storage.history(task['id']))

def report(task,body,files):
    current=guide(task);stage=body.get('stage');status=body.get('status')
    if stage not in {s['id'] for s in current['stages']} or status not in ('SELF_CHECKED','NEEDS_WORK','REPEAT_REQUESTED'):raise ValueError('Укажите этап и результат самостоятельной проверки')
    confirmed=body.get('confirmed',[])
    if not isinstance(confirmed,list) or any(type(i) is not int or i<0 or i>=len(current['requirements']) for i in confirmed):raise ValueError('Неизвестный критерий проверки')
    if status=='SELF_CHECKED' and set(confirmed)!=set(range(len(current['requirements']))):raise ValueError('Проверьте все критерии перед положительной отметкой')
    details={key:body.get(key,'') for key in ('errorNotes','explanation','hints')}
    if any(not isinstance(value,str) or len(value)>8000 for value in details.values()):raise ValueError('Текст отметки должен содержать не более 8000 символов')
    memory=body.get('memory','not_checked')
    if memory not in ('not_checked','reviewed','errors','not_required'):raise ValueError('Неизвестная отметка проверки памяти')
    if status=='SELF_CHECKED' and memory=='errors':raise ValueError('Сначала исправьте отмеченные ошибки памяти')
    if task['section']=='lecture-theory' and status=='SELF_CHECKED' and not details['explanation'].strip():raise ValueError('Добавьте своё объяснение: оно является частью закрепления')
    reports={**current['reports'],stage:dict(status=status,confirmed=confirmed,memory=memory,**details)}
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
