import json
import os
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('MASTERY_DATA', ROOT)).resolve()
DAY_NAMES = ['operators', 'memory', 'templates-functions', 'template-classes-rtti', 'final-exam']
_CATALOG=None
_CATALOG_LOCK=threading.Lock()

def catalog(include_theory=False):
    # Course definitions are immutable during a server session. Learner files
    # remain uncached so edits made in an external IDE are always read from disk.
    global _CATALOG
    if _CATALOG is None:
        with _CATALOG_LOCK:
            if _CATALOG is None:
                result=[]
                for path in sorted((ROOT/'days').glob('day-*/*/**/exercise.json')):
                    item=json.loads(path.read_text(encoding='utf-8'))
                    item['_path']=str(path.parent);result.append(item)
                _CATALOG=tuple(sorted(result,key=lambda t:(t['day'],t['order'])))
    return [dict(item) for item in _CATALOG if include_theory or item.get('section')!='lecture-theory']

def get_task(task_id):
    return next((t for t in catalog(include_theory=True) if t['id'] == task_id), None)

def public_task(task):
    if task.get('version') == 2:
        allowed={'id','day','version','section','group','kind','level','number','title','prompt','maxPoints','required','minutes','order','tags','filePath','options','multiple','category','difficulty','runner','code','traceFields','diagnosisChoices','publicChecks','dependencies','fixtures','variant'}
        return {k:v for k,v in task.items() if k in allowed}
    return {k: v for k, v in task.items() if k not in {'answer', 'explanation', 'optionExplanations', 'hints', '_path', 'tests', 'prefix', 'suffix', 'staticChecks'}}

def student_dir(task):
    folder = DATA / 'student' / f"day-{task['day']:02}" / task['id']
    folder.mkdir(parents=True, exist_ok=True)
    # Refuse symlink escapes even on a locally modified workspace.
    if not folder.resolve().is_relative_to((DATA / 'student').resolve()):
        raise ValueError('Недопустимый путь решения')
    return folder

def student_files(task):
    folder = student_dir(task)
    names = ['notes.md'] if task.get('localMain') or task.get('localAssessment') else (['solution.hpp', 'solution.cpp', 'notes.md'] if task['kind'] in ('S', 'D', 'C') else ['notes.md'])
    names += [name for name in task.get('starterFiles', {}) if name not in names]
    files = {}
    for name in names:
        path = folder / name
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError('Недопустимый путь файла')
        if not path.exists():
            starter = task.get('starter', '// Напишите решение здесь.\n') if name == 'solution.hpp' else '// Дополнительные определения. Подключите solution.hpp, если это необходимо.\n'
            if name == 'notes.md': starter = ''
            if name in task.get('starterFiles', {}): starter = task['starterFiles'][name]
            inherited=task.get('inheritFiles',{}).get(name)
            if inherited:
                previous=get_task(inherited['task'])
                base=(DATA/'student'/f"day-{previous['day']:02}"/previous['id']/inherited['name']) if previous else None
                if base and base.exists():
                    if base.is_symlink() or not base.resolve().is_relative_to((DATA/'student').resolve()):raise ValueError('Недопустимый путь исходного решения')
                    starter=base.read_text(encoding='utf-8')
            path.write_text(starter, encoding='utf-8')
        files[name] = path.read_text(encoding='utf-8')
    return files
