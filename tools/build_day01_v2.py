"""Prepare the current Day 1 course without overwriting student work."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,DATA,student_files
from tools.content.day01_v2.common import TASKS,PREAMBLE

DAY=ROOT/'days/day-01-operators'
NEW=DAY/'practice-v2'
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
def main():
    from tools.content.day01_v2 import questions,syntax,debugging,practice
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
    metadata={'version':2,'active':True,'project':'StereoLab','maximumPoints':130,'taskIds':[t['id'] for t in TASKS],'counts':{g:sum(t['group']==g for t in TASKS) for g in ('Q','S','P','D','A','B','C')}}
    # Activation comes last so an interrupted build cannot expose half a course.
    write(NEW/'manifest.json',json.dumps(metadata,ensure_ascii=False,indent=2))
    rows='\n'.join(f"| {t['id']} | {t['group']} | {t['title']} | {t['maxPoints']} |" for t in TASKS)
    write(DAY/'README.md','# День 1 · StereoLab: обработка стереосигнала\n\nНовая практика v2: Q16, S14, P6, D6, A3, B2, C1. Максимум 130 баллов.\n\nУтверждённая теория и четыре закрепления сохранены в `theory/lecture-01/`.\n\nМаршрут: понимание → синтаксис → трассировка → отладка → компоненты → интеграция → испытание. Свободная навигация сохраняется.\n\nA2/A3 проверяются автономно с минимальными тестовыми зависимостями. B/C компилируют только ваши A1–A3 и B1–B2.\n\n| ID | Этап | Задание | Максимум баллов |\n|---|---|---|---|\n'+rows+'\n')
    print(f'Day 1 StereoLab: {len(TASKS)} tasks, 130 points. Student files preserved.')

if __name__=='__main__':main()
