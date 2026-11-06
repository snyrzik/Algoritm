"""Remove explicitly selected legacy teaching files. Learner files and results are never deleted."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,catalog

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--modules',type=int,nargs='+',choices=[2,3,4,5],required=True);args=parser.parse_args();modules=set(args.modules)
    old=[task for task in catalog(True) if task['day'] in modules and not task.get('packLecture')]
    manifest=ROOT/'content/retired-practice.json'
    records={item['id']:item for item in json.loads(manifest.read_text(encoding='utf-8'))} if manifest.exists() else {}
    for task in old:records[task['id']]={key:task[key] for key in ('id','day','title','filePath')}
    manifest.parent.mkdir(exist_ok=True);manifest.write_text(json.dumps(list(records.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    targets=[name for name in tracked if any(name.startswith(f'days/day-{number:02}-') for number in modules) and '/lectures/' not in name]
    for name in targets:
        if not (ROOT/name).resolve().is_relative_to(ROOT.resolve()):raise ValueError('Teaching path escaped repository')
    for offset in range(0,len(targets),60):subprocess.run(['git','rm','--quiet','--',*targets[offset:offset+60]],cwd=ROOT,check=True)
    protection=ROOT/'tests/course_content.sha256.json';protected=json.loads(protection.read_text(encoding='utf-8'))
    protected={name:digest for name,digest in protected.items() if name not in targets}
    protection.write_text(json.dumps(protected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for number in modules:
        if number not in (2,3):continue
        folder=next((ROOT/'days').glob(f'day-{number:02}-*'))
        (folder/'README.md').write_text(f'# Лекция № {number}\n\nАвторский модуль: четыре главы и четыре закрепления.\n\nОткрыть: http://127.0.0.1:8765/#/theory/{number}/overview\n\nИсходный текст и проверочные MAIN находятся в content/lectures-02-03/. Решения ученик пишет самостоятельно. Прежние условия и проверки практикума удалены; личные файлы и результаты сохраняются.\n',encoding='utf-8',newline='\n')
    print(f'Removed {len(old)} legacy exercises and {len(targets)} teaching files. Learner sources and SQLite records preserved.')

if __name__=='__main__':main()
