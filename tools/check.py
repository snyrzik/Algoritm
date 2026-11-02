import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import catalog,student_files
from backend.compiler import doctor
from backend.grading import grade
from backend.storage import record

def main():
    p=argparse.ArgumentParser(description='C++ Mastery: реальная проверка файлов student/')
    p.add_argument('--doctor',action='store_true'); p.add_argument('--task'); p.add_argument('--day',type=int,choices=range(1,6)); p.add_argument('--compile',action='store_true'); p.add_argument('--no-record',action='store_true')
    args=p.parse_args()
    if args.doctor:
        report=doctor(); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['available'] else 2
    if not args.task and not args.day: p.error('Укажите --task d1-s01 или --day 1, либо --doctor')
    tasks=[t for t in catalog() if t['kind'] in ('S','D','C') and (t['id']==args.task if args.task else t['day']==args.day)]
    if not tasks: p.error('Задание не найдено или не содержит C++')
    failed=0
    for t in tasks:
        files=student_files(t); result=grade(t,files,'compile' if args.compile else 'test')
        if not args.no_record: result=record(t['id'],result['mode'],result,files)
        print(f"{t['id']} {t['title']}: {result['status']} ({result['score']}%)")
        for test in result['tests']: print(f"  {'PASS' if test['passed'] else 'FAIL'} {test['name']}"+ ('\n'+test['output'] if not test['passed'] else ''))
        if not result.get('compiled'): print(result.get('compilation',result.get('message','')))
        for e in result.get('staticErrors',[]): print('STATIC:',e)
        failed+=result['status'] not in ('PASS','COMPILED')
    return 1 if failed else 0

if __name__=='__main__': raise SystemExit(main())
