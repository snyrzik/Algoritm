"""Navigation and bookmarks, kept apart from assessment results."""
import json
import re
from . import storage
from .catalog import catalog

def state():
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS learner_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        values={row[0]:json.loads(row[1]) for row in db.execute('SELECT key,value FROM learner_state')}
    valid={task['id'] for task in catalog(True)}
    return dict(bookmarks=[key for key in values.get('bookmarks',[]) if key in valid],lastPath=values.get('lastPath',''))

def update(body):
    if not isinstance(body,dict) or not body or set(body)-{'bookmarks','lastPath'}:raise ValueError('Неизвестная настройка обучения')
    valid={task['id'] for task in catalog(True)}
    if 'bookmarks' in body:
        keys=body['bookmarks']
        if not isinstance(keys,list) or len(keys)>len(valid) or any(not isinstance(key,str) or key not in valid for key in keys):raise ValueError('Закладка должна указывать на существующее задание')
        body={**body,'bookmarks':list(dict.fromkeys(keys))}
    if 'lastPath' in body:
        path=body['lastPath']
        if not isinstance(path,str) or len(path)>500:raise ValueError('Недопустимый учебный маршрут')
        task_path=path.startswith('task/') and path[5:] in valid
        lecture_path=bool(re.fullmatch(r'theory/1/(?:overview|chapter-[1-5]|summary|practice|local-checks)(?:/[\w%.-]+)?',path))
        module_path=bool(re.fullmatch(r'module/[1-5]',path))
        if path and not (task_path or lecture_path or module_path):raise ValueError('Учебная страница не найдена')
    with storage.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS learner_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        for key,value in body.items():
            db.execute('INSERT INTO learner_state VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value,ensure_ascii=False)))
    return state()
