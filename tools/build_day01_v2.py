"""Materialize only the approved replacement Day 1. Migration is additive."""
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,DATA,student_files
from tools.content.day01_v2.common import TASKS,PREAMBLE

DAY=ROOT/'days/day-01-operators'
NEW=DAY/'practice-v2'
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
def archive_legacy():
    legacy=[]
    for path in DAY.glob('*/**/exercise.json'):
        task=json.loads(path.read_text(encoding='utf-8'))
        if task['id'].startswith('d1-') and task.get('section')!='lecture-theory':legacy.append(task)
    archive=DATA/'student/archive/day-01-v1';archive.mkdir(parents=True,exist_ok=True)
    manifest=archive/'migration.json'
    if not manifest.exists():
        copied={}
        for task in legacy:
            source=DATA/'student/day-01'/task['id']
            if not source.is_dir():continue
            for path in source.rglob('*'):
                if not path.is_file():continue
                if not path.resolve().is_relative_to((DATA/'student').resolve()):raise ValueError('Student path escapes workspace')
                target=archive/task['id']/path.relative_to(source)
                target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():shutil.copy2(path,target)
                copied[target.relative_to(archive).as_posix()]=hashlib.sha256(target.read_bytes()).hexdigest()
        backup=DATA/'progress/archive/day-01-v1-before-stereolab.sqlite3'
        database=DATA/'progress/mastery.sqlite3'
        if database.exists() and not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            old=sqlite3.connect(database);new=sqlite3.connect(backup)
            try:old.backup(new)
            finally:new.close();old.close()
        write(manifest,json.dumps({'created':datetime.now(timezone.utc).isoformat(),'taskIds':sorted(t['id'] for t in legacy),'files':copied,'originalsRetained':True},ensure_ascii=False,indent=2))
    return sorted(t['id'] for t in legacy)

def main():
    from tools.content.day01_v2 import questions,syntax,debugging,practice
    old_ids=archive_legacy()
    if sum(t['maxPoints'] for t in TASKS)!=130:raise ValueError('Scoring total must be 130')
    for task in TASKS:
        task['filePath']=f"student/day-01/{task['id']}/"+('main.cpp' if task['runner']=='console' else 'solution.hpp')
        if task['kind']=='P':task['starterFiles']={'answer.json':json.dumps({'output':'','explanation':'','trace':{},'variant':0},ensure_ascii=False)}
        if task['kind'] in ('S','D','C'):
            task['staticChecks']=['day1_no_resources']
        folder=NEW/task['group']/task['id'];folder.mkdir(parents=True,exist_ok=True)
        write(folder/'exercise.json',json.dumps(task,ensure_ascii=False,indent=2))
        # Public README contains only the condition, never the closed keys.
        write(folder/'README.md',f"# {task['title']}\n\n{task['prompt'].rstrip()}\n")
        if task['runner']=='cpp':
            functions='\n'.join(f'void test_{i}(){{\n{case["code"]}\n}}' for i,case in enumerate(task['tests']))
            switches='\n'.join(f'case {i}:test_{i}();break;' for i in range(len(task['tests'])))
            content='#include "candidate.hpp"\n'+PREAMBLE+'''
#undef CHECK
#define CHECK(...) do {if(!(__VA_ARGS__))throw std::runtime_error("Contract not satisfied; see the named check");}while(false)
'''+task.get('checks','')+'\n'+functions+'''
int main(int argc,char** argv){
    if(argc!=2)return 2;
    try{
        {std::ostringstream warm;warm<<std::setprecision(3)<<1.25;
         std::istringstream input("1.25 2");double decimal=0;int integer=0;input>>decimal>>integer;}
        const auto before=mastery_memory::live;
        switch(std::stoi(argv[1])){
'''+switches+'''
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
'''
            write(NEW/'tests'/f"{task['id']}.cpp",content)
            probe='#include "candidate.hpp"\n'+PREAMBLE+task.get('checks','')+'\nint main(){return 0;}\n'
            write(NEW/'tests'/f"{task['id']}-types.cpp",probe)
        student_files(task)
    if not (DAY/'archive/v1/README.md').exists():
        write(DAY/'archive/v1/README.md',(DAY/'README.md').read_text(encoding='utf-8'))
    metadata={'version':2,'active':True,'project':'StereoLab','maximumPoints':130,'legacyIds':old_ids,'taskIds':[t['id'] for t in TASKS],'counts':{g:sum(t['group']==g for t in TASKS) for g in ('Q','S','P','D','A','B','C')}}
    # Activation comes last so an interrupted build cannot expose half a course.
    write(NEW/'manifest.json',json.dumps(metadata,ensure_ascii=False,indent=2))
    rows='\n'.join(f"| {t['id']} | {t['group']} | {t['title']} | {t['maxPoints']} |" for t in TASKS)
    write(DAY/'README.md','# День 1 · StereoLab: обработка стереосигнала\n\nНовая практика v2: Q16, S14, P6, D6, A3, B2, C1. Максимум 130 баллов.\n\nУтверждённая теория и четыре закрепления сохранены в `theory/lecture-01/`. Старые задания доступны в архиве; их решения и история не удаляются и не засчитываются в новую версию.\n\nМаршрут: понимание → синтаксис → трассировка → отладка → компоненты → интеграция → испытание. Свободная навигация сохраняется.\n\nA2/A3 проверяются автономно с минимальными тестовыми зависимостями. B/C компилируют только ваши A1–A3 и B1–B2.\n\n| ID | Этап | Задание | Максимум баллов |\n|---|---|---|---|\n'+rows+'\n')
    print(f'Day 1 StereoLab: {len(TASKS)} new tasks, 130 points. {len(old_ids)} legacy tasks archived, no student files deleted.')

if __name__=='__main__':main()
