"""Lecture 1: the supplied author Markdown is preserved byte for byte."""
import hashlib
import json
import re
from .catalog import ROOT, get_task, public_task
from . import storage

LECTURE = ROOT / 'days' / 'day-01-operators' / 'theory' / 'lecture-01'
CHECK_IDS = [f'l01-v3-c{i:02}' for i in range(1,6)]
PROJECT_IDS = [f'l01-v3-p{i:02}' for i in range(1,4)]

def reading():
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS lecture_reading (section TEXT PRIMARY KEY, completed INTEGER NOT NULL)')
        return [row[0] for row in db.execute('SELECT section FROM lecture_reading WHERE completed=1 ORDER BY section')]

def mark_read(section, completed):
    if section not in {f'chapter-{i}' for i in range(1,6)} or type(completed) is not bool:
        raise ValueError('Укажите главу 1–5 и отметку прочтения')
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS lecture_reading (section TEXT PRIMARY KEY, completed INTEGER NOT NULL)')
        db.execute('INSERT INTO lecture_reading VALUES(?,?) ON CONFLICT(section) DO UPDATE SET completed=excluded.completed', (section,int(completed)))
    return reading()

def lecture():
    content = (LECTURE / 'theory.md').read_bytes()
    markdown = content.decode('utf-8')
    boundaries = list(re.finditer(r'^# (Глава [1-5]\..+|Итоги теории первой лекции)\r?$', markdown, re.M))
    if len(boundaries) != 6:
        raise ValueError('В лекции должны быть пять глав и раздел итогов')
    sections = [dict(id='overview', title='О лекции', markdown=markdown[:boundaries[0].start()])]
    for i, match in enumerate(boundaries):
        end = boundaries[i+1].start() if i+1 < len(boundaries) else len(markdown)
        item = dict(id=f'chapter-{i+1}' if i<5 else 'summary', title=match[1], markdown=markdown[match.start():end])
        if i<5:
            item['chapter'] = i+1
            item['checkId'] = CHECK_IDS[i]
        sections.append(item)
    return dict(id='lecture-01-v3',day=1,lecture=1,title='Перегрузка операций',sourceFilename='Lecture_01_FULL_THEORY.md',sourceSha256=hashlib.sha256(content).hexdigest(),sections=sections,checks=[public_task(get_task(key)) for key in CHECK_IDS],projects=[public_task(get_task(key)) for key in PROJECT_IDS],localInstructions=(LECTURE/'local-checks/README.md').read_text(encoding='utf-8'),reading=reading())

def project_guide(task):
    source=(LECTURE/task['localMain']).read_bytes().decode('utf-8')
    cases=[dict(id=f'case-{i:02}',name=name) for i,name in enumerate(task['publicChecks'],1)]
    return dict(task=task['id'],mode='self-check',main=source,originalCode='',expectedOutput=task['expectedOutput'],console=False,assertBased=True,guideHash=hashlib.sha256(source.encode()).hexdigest(),cases=cases,extraFiles=[],dependencies=[],instructions='Добавьте этот main.cpp к своим файлам '+task['project']+'.hpp и '+task['project']+'.cpp. Проверка запускается только в вашей IDE. Не определяйте NDEBUG: assert должен оставаться включённым.',review=['Этот main проверяет основные сценарии; он не заменяет анализ памяти, граничных случаев и требований ЛР № 1.','Ручная отметка сообщает только о выполненной вами базовой проверке.'])

def summary():
    latest={}
    for item in storage.history(): latest.setdefault(item['task'],item)
    done=lambda ids:sum(latest.get(key,{}).get('status')=='SELF_CHECKED' for key in ids)
    return dict(version=3,reading=len(reading()),chapters=5,checks=done(CHECK_IDS),checkTotal=5,projects=done(PROJECT_IDS),projectTotal=3,completed=done(CHECK_IDS+PROJECT_IDS),total=8)
