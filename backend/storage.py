import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from .catalog import DATA

PROFILE_LOCK=threading.Lock()
DB_LOCK=threading.RLock()

def profile_id():
    """A new data directory must not restore drafts from an older browser profile."""
    with PROFILE_LOCK:
        folder=DATA/'progress';folder.mkdir(parents=True,exist_ok=True)
        path=folder/'workspace-id'
        if not path.exists():path.write_text(uuid.uuid4().hex,encoding='ascii')
        return path.read_text(encoding='ascii').strip()

@contextmanager
def connect():
    # HTTP workers may initialize tables and update navigation concurrently.
    # Serialize these short local transactions to avoid read-to-write lock upgrades.
    with DB_LOCK:
        (DATA / 'progress').mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(DATA / 'progress' / 'mastery.sqlite3', timeout=20)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, task TEXT NOT NULL, created TEXT NOT NULL, mode TEXT NOT NULL, result TEXT NOT NULL, snapshot TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS hints (id INTEGER PRIMARY KEY, task TEXT NOT NULL, created TEXT NOT NULL, level INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY, started REAL NOT NULL, duration INTEGER NOT NULL, timed INTEGER NOT NULL, finished REAL, tasks TEXT NOT NULL)')
            with db:
                yield db
        finally:
            db.close()

def now(): return datetime.now(timezone.utc).isoformat()

def record(task, mode, result, snapshot):
    with connect() as db:
        count = db.execute('SELECT COUNT(*) FROM hints WHERE task=?', (task,)).fetchone()[0]
        result = {**result, 'hintsUsed': count}
        cur = db.execute('INSERT INTO attempts(task,created,mode,result,snapshot) VALUES(?,?,?,?,?)', (task, now(), mode, json.dumps(result, ensure_ascii=False), json.dumps(snapshot, ensure_ascii=False)))
        result['attemptId'] = cur.lastrowid
        return result

def history(task=None):
    with connect() as db:
        rows = db.execute('SELECT id,task,created,mode,result FROM attempts' + (' WHERE task=?' if task else '') + ' ORDER BY id DESC', (task,) if task else ()).fetchall()
    return [{**json.loads(r[4]), 'id':r[0], 'task':r[1], 'created':r[2], 'mode':r[3]} for r in rows]

def hint(task, level):
    with connect() as db:
        db.execute('INSERT INTO hints(task,created,level) VALUES(?,?,?)', (task, now(), level))

def snapshot(attempt_id):
    with connect() as db:
        row = db.execute('SELECT task,snapshot FROM attempts WHERE id=?', (attempt_id,)).fetchone()
    return {'task': row[0], 'files': json.loads(row[1])} if row else None
