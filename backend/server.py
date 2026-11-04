import json
import mimetypes
import os
import random
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from . import storage
from .catalog import ROOT, DATA, catalog, get_task, public_task, student_files, student_dir
from .answers import grade_answer, revision
from .self_check import guide,report,bundle

TOKEN=secrets.token_urlsafe(32)
LOCKS={}
LOCKS_GUARD=threading.Lock()

def task_lock(task_id):
    with LOCKS_GUARD: return LOCKS.setdefault(task_id,threading.RLock())

def exam_state():
    with storage.connect() as db:
        row=db.execute('SELECT id,started,duration,timed,finished,tasks FROM exams ORDER BY id DESC LIMIT 1').fetchone()
        if row and row[3] and not row[4] and time.time()>=row[1]+row[2]:
            db.execute('UPDATE exams SET finished=? WHERE id=?',(row[1]+row[2],row[0]))
            row=(*row[:4],row[1]+row[2],row[5])
    return None if not row else dict(id=row[0],started=row[1],duration=row[2],timed=bool(row[3]),finished=row[4],tasks=json.loads(row[5]),serverTime=time.time())

def check_exam(task):
    exam=exam_state()
    if task['day']==5 and exam and exam['timed'] and exam['finished']:
        raise ValueError('Экзаменационная сессия завершена. Начните новую сессию или тренировку без таймера.')
    if task['day']==5 and exam and exam['timed'] and task['kind']=='S':
        # Each syntax item has a persistent, server-owned start time. Refreshing
        # or switching tasks cannot reset the budget within this exam session.
        with storage.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS syntax_clock (exam INTEGER,task TEXT,started REAL,PRIMARY KEY(exam,task))')
            db.execute('INSERT OR IGNORE INTO syntax_clock VALUES(?,?,?)',(exam['id'],task['id'],time.time()))
            started=db.execute('SELECT started FROM syntax_clock WHERE exam=? AND task=?',(exam['id'],task['id'])).fetchone()[0]
        if time.time()-started>240: raise ValueError('Лимит 4 минуты на этот синтаксический вопрос истёк. Продолжите экзамен или начните тренировочную сессию.')

def syntax_deadline(task):
    exam=exam_state()
    if not exam or not exam['timed'] or exam['finished'] or task['day']!=5 or task['kind']!='S': return None
    with storage.connect() as db:
        row=db.execute('SELECT started FROM syntax_clock WHERE exam=? AND task=?',(exam['id'],task['id'])).fetchone()
    return row[0]+240 if row else None

class Handler(BaseHTTPRequestHandler):
    server_version='CppMastery/1.0'
    def log_message(self,format,*args):
        if args and str(args[0]).startswith(('GET /api','PUT /api','POST /api')): return
        super().log_message(format,*args)

    def send_json(self,value,status=200):
        payload=json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def allowed(self,write=False):
        if self.headers.get('Sec-Fetch-Site')=='cross-site': return False
        host=self.headers.get('Host','').split(':')[0]
        if host not in ('127.0.0.1','localhost'): return False
        origin=self.headers.get('Origin')
        if origin:
            u=urlparse(origin)
            if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.port not in (5173,self.server.server_port): return False
        return not write or secrets.compare_digest(self.headers.get('X-Mastery-Token',''),TOKEN)

    def do_GET(self):
        try:
            if not self.allowed(): return self.send_json({'error':'Локальный доступ запрещён'},403)
            path=urlparse(self.path).path
            parts=path.strip('/').split('/')
            if path=='/api/session': return self.send_json({'token':TOKEN,'profileId':storage.profile_id()})
            if path=='/api/day01/summary':
                from .theory import summary
                return self.send_json(summary())
            if path=='/api/theory/day-1/lecture-1':
                from .theory import lecture
                return self.send_json(lecture())
            if path=='/api/course':
                return self.send_json({'days':json.loads((ROOT/'days/course.json').read_text(encoding='utf-8')),'tasks':[public_task(t) for t in catalog(include_theory=True)]})
            if path=='/api/learning':
                from .learning import state
                return self.send_json(state())
            if path=='/api/doctor': return self.send_json({'error':'Используется самостоятельная проверка без встроенного компилятора'},410)
            if path=='/api/progress':
                from .theory import reading
                return self.send_json({'attempts':storage.history(),'exam':exam_state(),'reading':reading()})
            if len(parts)==3 and parts[:2]==['api','self-check']:
                task=get_task(parts[2])
                if not task:return self.send_json({'error':'Задание не найдено'},404)
                return self.send_json(guide(task))
            if len(parts)==3 and parts[:2]==['api','self-check-bundle']:
                task=get_task(parts[2])
                if not task:return self.send_json({'error':'Задание не найдено'},404)
                with task_lock(task['id']):payload=bundle(task)
                self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition',f'attachment; filename="{task["id"]}-check.zip"');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload);return
            if len(parts)==3 and parts[:2]==['api','task']:
                task=get_task(parts[2])
                if not task: return self.send_json({'error':'Задание не найдено'},404)
                with task_lock(task['id']): files=student_files(task)
                # Opening a timed syntax item starts its clock before editing.
                timer_error=None
                try: check_exam(task)
                except ValueError as exc: timer_error=str(exc)
                names=[{'name':name,'category':'contract'} for name in task.get('publicChecks',[])] if task.get('version')==2 else [{'name':t['name'],'category':t['category']} for t in task.get('tests',[])]
                return self.send_json({'task':public_task(task),'files':files,'revision':revision(files),'history':storage.history(task['id']),'context':{'before':task.get('prefix',''),'after':task.get('suffix','')},'testNames':names,'timerError':timer_error,'syntaxDeadline':syntax_deadline(task)})
            if len(parts)==3 and parts[:2]==['api','snapshot']:
                value=storage.snapshot(int(parts[2]))
                return self.send_json(value or {'error':'Попытка не найдена'},200 if value else 404)
            if len(parts)==3 and parts[:2]==['api','review']:
                task=get_task(parts[2])
                if not task or not any(a['mode']=='answer' for a in storage.history(parts[2])): return self.send_json({'error':'Разбор доступен после ответа'},403)
                exam=exam_state()
                if exam and exam['timed'] and not exam['finished'] and task['day']==5: return self.send_json({'deferred':True,'message':'Разбор откроется после завершения экзамена.'})
                return self.send_json({k:task[k] for k in ('answer','explanation','optionExplanations')})
            if path.startswith('/api/'): return self.send_json({'error':'Маршрут не найден'},404)
            root=(ROOT/'app/dist').resolve()
            target=(root/path.lstrip('/')).resolve()
            if not target.is_relative_to(root): return self.send_json({'error':'Недопустимый путь'},403)
            if not target.is_file(): target=root/'index.html'
            if not target.is_file(): return self.send_json({'error':'Сначала выполните npm run build или npm run dev.'},503)
            payload=target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',mimetypes.guess_type(target)[0] or 'application/octet-stream')
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','same-origin')
            self.end_headers(); self.wfile.write(payload)
        except (ValueError,KeyError) as exc: self.send_json({'error':str(exc)},400)
        except (BrokenPipeError,ConnectionResetError): pass
        except Exception as exc: self.send_json({'error':f'Ошибка сервера: {exc}'},500)

    def do_PUT(self): self.mutate()
    def do_POST(self): self.mutate()

    def mutate(self):
        try:
            if not self.allowed(True): return self.send_json({'error':'Нужна локальная сессия и корректный токен'},403)
            length=int(self.headers.get('Content-Length',0))
            if length<0 or length>1024*1024: return self.send_json({'error':'Лимит запроса — 1 МБ'},413)
            if 'application/json' not in self.headers.get('Content-Type',''): return self.send_json({'error':'Ожидается JSON'},415)
            body=json.loads(self.rfile.read(length) or '{}')
            path=urlparse(self.path).path
            if path=='/api/learning':
                from .learning import update
                return self.send_json(update(body))
            if path=='/api/exam/start':
                tasks=[t['id'] for t in catalog() if t['day']==5 and t['kind']=='S']
                random.SystemRandom().shuffle(tasks)
                timed=bool(body.get('timed',False))
                with storage.connect() as db:
                    db.execute('UPDATE exams SET finished=? WHERE finished IS NULL',(time.time(),))
                    db.execute('INSERT INTO exams(started,duration,timed,tasks) VALUES(?,?,?,?)',(time.time(),6*3600,int(timed),json.dumps(tasks)))
                return self.send_json(exam_state())
            if path=='/api/exam/finish':
                with storage.connect() as db: db.execute('UPDATE exams SET finished=? WHERE finished IS NULL',(time.time(),))
                return self.send_json(exam_state())
            parts=path.strip('/').split('/')
            if len(parts)!=3: return self.send_json({'error':'Маршрут не найден'},404)
            if parts[:2]==['api','lecture-read']:
                from .theory import mark_read
                return self.send_json({'reading':mark_read(parts[2],body.get('completed'))})
            task=get_task(parts[2])
            if not task: return self.send_json({'error':'Задание не найдено'},404)
            action=parts[1]
            with task_lock(task['id']):
                if action=='files':
                    old=student_files(task)
                    if body.get('revision')!=revision(old): return self.send_json({'error':'Файлы изменены вне редактора. Ваш черновик сохранён в браузере; загрузите файлы с диска или скопируйте черновик перед объединением.','conflict':True},409)
                    incoming=body.get('files')
                    if not isinstance(incoming,dict) or set(incoming)!=set(old): raise ValueError('Недопустимый набор файлов')
                    if any(not isinstance(v,str) or len(v.encode('utf-8'))>256*1024 for v in incoming.values()): raise ValueError('Файл превышает 256 КБ или не является текстом')
                    folder=student_dir(task)
                    for name,value in incoming.items():
                        temp=folder/(name+'.tmp')
                        if temp.is_symlink(): raise ValueError('Недопустимый временный путь')
                        temp.write_text(value,encoding='utf-8'); os.replace(temp,folder/name)
                    return self.send_json({'revision':revision(incoming)})
                if action=='hint':
                    exam=exam_state()
                    if task['day']==5 and exam and exam['timed'] and not exam['finished']: return self.send_json({'error':'Подсказки отключены в экзаменационной сессии'},403)
                    level=body.get('level',1)
                    if type(level) is not int or level<1 or level>3: raise ValueError('Уровень подсказки: 1–3')
                    storage.hint(task['id'],level)
                    return self.send_json({'text':task['hints'][level-1],'level':level})
                if action=='answer':
                    if task['kind'] not in ('Q','P'): raise ValueError('Для этого задания используйте самостоятельную проверку')
                    check_exam(task)
                    result=grade_answer(task,body.get('answer'))
                    if task.get('version')==2:result.update(pointsEarned=1 if result['status']=='PASS' else 0,maxPoints=1)
                    return self.send_json(storage.record(task['id'],'answer',result,{'answer':body['answer']}))
                if action=='self-check':
                    check_exam(task)
                    files=student_files(task)
                    result=report(task,body,files)
                    return self.send_json(storage.record(task['id'],'self-check',result,files))
                if action=='run':return self.send_json({'error':'Встроенная компиляция отключена. Откройте main для самостоятельной проверки.'},410)
                return self.send_json({'error':'Маршрут не найден'},404)
        except (ValueError,TypeError,KeyError) as exc: self.send_json({'error':str(exc)},400)
        except (BrokenPipeError,ConnectionResetError): pass
        except Exception as exc: self.send_json({'error':f'Ошибка сервера: {exc}'},500)

def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    server.daemon_threads=True
    print(f'C++ Mastery: http://127.0.0.1:{args.port}/#/day/1',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
