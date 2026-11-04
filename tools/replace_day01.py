"""Remove superseded Day 1 learner data only, as requested. Never touches other days."""
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import DATA

def obsolete(task):
    return task.startswith(('d01-v2-','d1-'))

def replace(root=DATA):
    root=Path(root).resolve()
    dbpath=root/'progress/mastery.sqlite3'
    if dbpath.exists() and (dbpath.is_symlink() or not dbpath.resolve().is_relative_to(root)):raise ValueError('Linked progress database')
    base=root/'student/day-01'
    files=[];folders=[]
    if base.exists():
        if base.is_symlink() or not base.resolve().is_relative_to(root):raise ValueError('Linked learner directory')
        for folder in base.iterdir():
            if not obsolete(folder.name):continue
            if not folder.is_dir() or folder.is_symlink():raise ValueError('Unexpected learner entry')
            for path in folder.rglob('*'):
                if path.is_symlink() or not path.resolve().is_relative_to(base):raise ValueError('Learner path escapes Day 1')
                if path.is_file():files.append(path)
                elif path.is_dir():folders.append(path)
            folders.append(folder)
    for path in files:path.unlink()
    for path in sorted(folders,key=lambda p:len(p.parts),reverse=True):path.rmdir()
    removed=0
    if dbpath.exists():
        if dbpath.is_symlink() or not dbpath.resolve().is_relative_to(root):raise ValueError('Linked progress database')
        with closing(sqlite3.connect(dbpath)) as db, db:
            for table in ('attempts','hints'):
                if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():
                    removed+=db.execute(f"DELETE FROM {table} WHERE task GLOB 'd01-v2-*' OR task GLOB 'd1-*'").rowcount
    return dict(deletedFiles=len(files),deletedResults=removed,otherDays='preserved')

if __name__=='__main__':print(json.dumps(replace()))
