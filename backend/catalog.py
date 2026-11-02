import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('MASTERY_DATA', ROOT)).resolve()
DAY_NAMES = ['operators', 'memory', 'templates-functions', 'template-classes-rtti', 'final-exam']

def catalog(include_theory=False):
    result = []
    for path in sorted((ROOT / 'days').glob('day-*/*/**/exercise.json')):
        item = json.loads(path.read_text(encoding='utf-8'))
        if item.get('section') == 'lecture-theory' and not include_theory:
            continue
        item['_path'] = str(path.parent)
        result.append(item)
    return sorted(result, key=lambda t: (t['day'], t['order']))

def get_task(task_id):
    return next((t for t in catalog(include_theory=True) if t['id'] == task_id), None)

def public_task(task):
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
    names = ['solution.hpp', 'solution.cpp', 'notes.md'] if task['kind'] in ('S', 'D', 'C') else ['notes.md']
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
            path.write_text(starter, encoding='utf-8')
        files[name] = path.read_text(encoding='utf-8')
    return files
