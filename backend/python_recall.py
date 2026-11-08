"""Independent Python subject: saved text and learner marks, never code execution."""
import io
import json
import os
import re
import zipfile
from functools import lru_cache
from .catalog import ROOT,DATA
from .answers import revision
from . import storage

SOURCE=ROOT/'content/python-recall'
PRIVATE=ROOT/'.private/python-recall/import/private_solutions.json'
PUBLIC_FIELDS={'id','number','week','day','week_title','title','difficulty','minutes','skills','signature','description','rules','example','edges','bonus','sources_labels','source_urls','dependencies','kind','optional_topic','recommended_minutes_min','recommended_minutes_max','test_mode','starter_code','starter_files'}

@lru_cache(maxsize=1)
def catalog():
    return json.loads((SOURCE/'import/public_catalog.json').read_text(encoding='utf-8'))

def task(key):
    value=next((t for t in catalog()['tasks'] if t['id']==key),None)
    if value is None:raise ValueError('Задача Python не найдена')
    return value

def public_task(value):
    return {k:v for k,v in value.items() if k in PUBLIC_FIELDS}

def folder(value):
    path=DATA/'student/python'/value['id']
    if path.is_symlink() or not path.resolve().is_relative_to((DATA/'student').resolve()):raise ValueError('Недопустимый путь Python')
    path.mkdir(parents=True,exist_ok=True)
    return path

def files(value):
    result={};base=folder(value)
    for name,starter in value['starter_files'].items():
        if not re.fullmatch(r'[A-Za-z0-9_-]+\.py',name):raise ValueError('Недопустимое имя исходника')
        path=base/name
        if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):raise ValueError('Недопустимый путь исходника')
        if not path.exists():path.write_text(starter,encoding='utf-8')
        result[name]=path.read_text(encoding='utf-8')
    return result

def save_files(value,body):
    old=files(value)
    if body.get('revision')!=revision(old):return None
    incoming=body.get('files')
    if not isinstance(incoming,dict) or incoming.keys()!=old.keys() or any(not isinstance(v,str) or len(v.encode())>256*1024 for v in incoming.values()):raise ValueError('Недопустимые файлы Python: сохраните исходные имена, лимит — 256 КБ')
    for name,text in incoming.items():
        target=folder(value)/name;temp=target.with_suffix('.py.tmp')
        if temp.is_symlink():raise ValueError('Недопустимый временный файл')
        temp.write_text(text,encoding='utf-8');os.replace(temp,target)
    return dict(revision=revision(incoming))

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS python_state (task TEXT PRIMARY KEY, value TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS python_attempts (id INTEGER PRIMARY KEY, task TEXT NOT NULL, created TEXT NOT NULL, qualified INTEGER NOT NULL, value TEXT NOT NULL, snapshot TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS python_learning (key TEXT PRIMARY KEY, value TEXT NOT NULL)')

def default_state():
    return dict(status='not_started',notes='',difficulty='',weakTopics=[],bookmark=False,skipped=False,topicReady=False,external=False,localChecked=False)

def state(key):
    with storage.connect() as db:
        initialize(db);row=db.execute('SELECT value FROM python_state WHERE task=?',(key,)).fetchone()
    return {**default_state(),**(json.loads(row[0]) if row else {})}

def history(key):
    with storage.connect() as db:
        initialize(db);rows=db.execute('SELECT id,created,qualified,value FROM python_attempts WHERE task=? ORDER BY id DESC',(key,)).fetchall()
    return [dict(id=r[0],created=r[1],qualified=bool(r[2]),**json.loads(r[3])) for r in rows]

def unlocked(key):
    with storage.connect() as db:
        initialize(db);return bool(db.execute('SELECT 1 FROM python_attempts WHERE task=? AND qualified=1 LIMIT 1',(key,)).fetchone())

def progress():
    with storage.connect() as db:
        initialize(db);states={key:json.loads(value) for key,value in db.execute('SELECT task,value FROM python_state')}
        learning={key:json.loads(value) for key,value in db.execute('SELECT key,value FROM python_learning')}
    return dict(states=states,lastPath=learning.get('lastPath','python'),manual=True)

def learning(body):
    if not isinstance(body,dict) or set(body)!={'lastPath'} or not isinstance(body['lastPath'],str):raise ValueError('Недопустимая настройка Python')
    path=body['lastPath']
    if not re.fullmatch(r'python(?:/(?:week/[1-8]|task/py-(?:0[1-9]|[1-3][0-9]|40)|search|saved|review|progress|help))?',path):raise ValueError('Страница Python не найдена')
    with storage.connect() as db:
        initialize(db);db.execute('INSERT INTO python_learning VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',('lastPath',json.dumps(path)))
    return progress()

def meaningful(value,sources):
    def normalize(text):
        return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    return any(normalize(sources[name])!=normalize(starter) for name,starter in value['starter_files'].items())

def mark(value,body):
    fields=set(default_state())
    if not isinstance(body,dict) or not body or set(body)-fields:raise ValueError('Недопустимая отметка Python')
    current={**state(value['id']),**body}
    if current['status'] not in ('not_started','in_progress','completed','revisit'):raise ValueError('Неизвестный статус')
    if not isinstance(current['notes'],str) or len(current['notes'])>8000:raise ValueError('Заметки: не более 8000 символов')
    if current['difficulty'] not in ('','easy','okay','hard'):raise ValueError('Неизвестная оценка сложности')
    if not isinstance(current['weakTopics'],list) or len(current['weakTopics'])>30 or any(not isinstance(t,str) or len(t)>100 for t in current['weakTopics']):raise ValueError('Недопустимые темы для повторения')
    if any(type(current[key]) is not bool for key in ('bookmark','skipped','topicReady','external','localChecked')):raise ValueError('Отметки должны быть логическими значениями')
    sources=files(value) if 'status' in body else None
    qualified=bool(sources and (meaningful(value,sources) or (current['external'] and len(current['notes'].strip())>=20)))
    if 'status' in body and current['status']=='completed' and not (qualified and current['localChecked']):raise ValueError('Для завершения нужна своя попытка и отметка о локальной проверке. Для работы в IDE добавьте объяснение не короче 20 символов.')
    with storage.connect() as db:
        initialize(db)
        db.execute('INSERT INTO python_state VALUES(?,?) ON CONFLICT(task) DO UPDATE SET value=excluded.value',(value['id'],json.dumps(current,ensure_ascii=False)))
        if 'status' in body:db.execute('INSERT INTO python_attempts(task,created,qualified,value,snapshot) VALUES(?,?,?,?,?)',(value['id'],storage.now(),int(qualified),json.dumps(current,ensure_ascii=False),json.dumps(sources,ensure_ascii=False)))
    return dict(state=current,solutionUnlocked=unlocked(value['id']),history=history(value['id']))

def detail(value):
    sources=files(value)
    return dict(task=public_task(value),files=sources,revision=revision(sources),history=history(value['id']),state=state(value['id']),solutionUnlocked=unlocked(value['id']),context=dict(before='',after=''),testNames=[])

def solution(value):
    if not unlocked(value['id']):return None
    if not PRIVATE.is_file():raise ValueError('Эталон пока недоступен в этом профиле установки')
    data=json.loads(PRIVATE.read_text(encoding='utf-8'))
    answer=next(t for t in data['tasks'] if t['id']==value['id'])
    return {key:answer[key] for key in ('id','solution_files','explanation','manual_review') if key in answer}

def bundle(value):
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,text in files(value).items():archive.writestr(name,text)
        archive.writestr('task.md',(SOURCE/value['task_md_file']).read_bytes())
        archive.writestr('LOCAL_RUN.md','Python 3.10+. Запускайте код только в своей IDE.\n\nДля функций создайте собственные вызовы или assert по примерам и граничным случаям условия. Для CLI/GUI запустите свой файл, для задачи 14 — python main.py.\n\nЗависимости этой задачи: '+(', '.join(value['dependencies']) or 'стандартная библиотека')+'.\n\nЭтот архив содержит ваши исходники и условие, без эталонного решения.\n')
    return output.getvalue()
