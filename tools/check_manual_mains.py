"""Optional development QA of downloadable mains. Not used by the application."""
import io
import os
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
TEMP=tempfile.TemporaryDirectory(prefix='mastery-manual-main-')
os.environ['MASTERY_DATA']=TEMP.name
from backend.catalog import DATA,catalog,get_task
from backend.self_check import bundle,guide
from backend.compiler import compile_cpp,execute,doctor,toolchain,run_process
sys.path.insert(0,str(ROOT/'tests'))
from day01_v2_helpers import S_REFERENCES,debug_reference,reference_files,seeded_components

THEORY={
1:'class ScoreCounter {public: explicit ScoreCounter(int=0); int points()const; ScoreCounter& add(int);}; bool higher_score(const ScoreCounter&,const ScoreCounter&);',
2:'class Duration {public: explicit Duration(int);int seconds()const;Duration& operator+=(const Duration&);Duration& operator++();Duration operator++(int);Duration operator-()const;};Duration operator+(const Duration&,const Duration&);bool operator==(const Duration&,const Duration&);bool operator!=(const Duration&,const Duration&);',
3:'class FixedHistory{public:FixedHistory(int,int,int,int);int& operator[](std::size_t);const int& operator[](std::size_t)const;int operator()(std::size_t,std::size_t)const;void swap_indices(std::size_t,std::size_t);};',
4:'class ClockTime{public:ClockTime(int,int);};std::ostream& operator<<(std::ostream&,const ClockTime&);std::istream& operator>>(std::istream&,ClockTime&);',
}

def unpack(task,folder,files=None):
    folder.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
        for item in archive.infolist():
            path=(folder/item.filename).resolve()
            if not path.is_relative_to(folder.resolve()):raise AssertionError('Unexpected archive path')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(item))
    for name,value in (files or {}).items():(folder/name).write_text(value,encoding='utf-8')

def runtime(task,files):
    folder=DATA/task['id'];unpack(task,folder,files)
    program=folder/'manual.exe'
    result=compile_cpp(sorted(folder.rglob('*.cpp')),program,[folder])
    if result['code']:raise AssertionError((task['id'],result['output']))
    current=guide(task)
    if current['console']:
        from backend.day01_v2.console import cases,evaluate
        for case in cases():
            result=execute(program,stdin_text=case['input'],separate_stderr=True)
            if not evaluate(case,result)[0]:raise AssertionError((task['id'],case['name'],result))
    else:
        result=execute(program)
        if result['code'] or result['output'].replace('\r\n','\n')!=current['expectedOutput']:raise AssertionError((task['id'],result,current['expectedOutput']))

def main():
    if not doctor()['available']:raise SystemExit('Optional developer check needs an available C++17 compiler; the app does not.')
    count=0
    try:
        with seeded_components():
            for number,source in S_REFERENCES.items():
                task=get_task(f'd01-v2-s{number:02}');runtime(task,{'solution.hpp':source,'solution.cpp':''});count+=1
            for number in range(1,7):
                task=get_task(f'd01-v2-d{number:02}');runtime(task,{'solution.hpp':debug_reference(task),'solution.cpp':''});count+=1
            for suffix in ('a01','a02','a03','b01','b02','c01'):
                task=get_task('d01-v2-'+suffix);files=reference_files(task['id']);files.pop('main.cpp',None);runtime(task,files);count+=1
        print(f'{count} mains: correct implementations produce the exact advertised output.',flush=True)
        # A deliberately incorrect implementation must disagree with the printed target.
        task=get_task('d01-v2-s10');folder=DATA/'mutant';unpack(task,folder,{'solution.hpp':'double operator()(double x)const{return a_*x+b_+c_;}','solution.cpp':''})
        program=folder/'mutant.exe';built=compile_cpp([folder/'main.cpp',folder/'solution.cpp'],program,[folder]);assert built['code']==0,built['output']
        result=execute(program);assert result['code']!=0 and ': FAIL:' in result['output']
        print('Wrong implementation: FAIL is printed; no false success.',flush=True)
        syntax_count=0;tc=toolchain()
        for task in catalog(include_theory=True):
            if task['kind']!='C' or task.get('version')==2:continue
            folder=DATA/('syntax-'+task['id']);unpack(task,folder)
            (folder/'support.hpp').write_text('#pragma once\n',encoding='utf-8')
            source=THEORY[task['chapter']] if task.get('section')=='lecture-theory' else '#include "contracts.hpp"\n'
            (folder/'solution.hpp').write_text(source,encoding='utf-8')
            includes=[folder,ROOT/'tests',ROOT/'tools']
            args=[tc['exe'],'/nologo','/std:c++17','/EHsc','/W4','/WX','/utf-8','/Zs',*[f'/I{p}' for p in includes],folder/'main.cpp'] if tc['kind']=='msvc' else [tc['exe'],'-std=c++17','-Wall','-Wextra','-Wconversion','-Wpedantic','-Werror','-fsyntax-only',*[f'-I{p}' for p in includes],folder/'main.cpp']
            result=run_process(args,folder,tc['env'],30)
            if result['code']:raise AssertionError((task['id'],result['output']))
            syntax_count+=1
        print(f'{syntax_count} further mains: API declaration and syntax checks passed (including all four lecture checks).',flush=True)
    finally:TEMP.cleanup()

if __name__=='__main__':main()
