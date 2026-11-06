"""Access to a learner's earlier files and results, without retired teaching content."""
import io
import json
import zipfile
from .catalog import ROOT,DATA
from . import storage

def records():
    path=ROOT/'content/retired-practice.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []

def folder(item):
    path=DATA/'student'/f"day-{item['day']:02}"/item['id']
    if path.is_symlink() or not path.resolve().is_relative_to((DATA/'student').resolve()):raise ValueError('Недопустимый путь сохранённых файлов')
    return path

def overview():
    history=storage.history();result=[]
    for item in records():
        path=folder(item);attempts=[row for row in history if row['task']==item['id']]
        if attempts or (path.exists() and any(path.iterdir())):result.append({**item,'attempts':attempts,'hasFiles':path.exists()})
    return result

def bundle():
    output=io.BytesIO();history=storage.history();ids={item['id'] for item in records()}
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for item in records():
            path=folder(item)
            if not path.exists():continue
            for source in path.rglob('*'):
                if source.is_symlink() or not source.resolve().is_relative_to(path.resolve()):raise ValueError('Недопустимый путь исходников')
                if source.is_file():archive.writestr(f"day-{item['day']:02}/{item['id']}/"+source.relative_to(path).as_posix(),source.read_bytes())
        archive.writestr('results.json',json.dumps([item for item in history if item['task'] in ids],ensure_ascii=False,indent=2))
        archive.writestr('index.json',json.dumps(records(),ensure_ascii=False,indent=2))
    return output.getvalue()
