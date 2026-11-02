import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path
from ..catalog import ROOT,DATA,get_task,student_files
from ..compiler import compile_cpp,execute,doctor
from .scoring import latest_diagnosis

FIXTURES=Path(__file__).with_name('fixtures')
TESTS=ROOT/'days/day-01-operators/practice-v2/tests'
NAMES={'d01-v2-a01':'StereoSample.hpp','d01-v2-a02':'ChannelMix.hpp','d01-v2-a03':'AudioBlock.hpp','d01-v2-b01':'StereoIO.hpp','d01-v2-b02':'StereoPipeline.hpp'}

def meaningful(source):
    return re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27','',source,flags=re.S).strip()

def finish(task,result,passed=0,total=0):
    maximum=task['maxPoints'];diagnostic=latest_diagnosis(task['id']) if task['kind']=='D' else None
    if task['kind']=='S':points=int(result.get('signaturePassed',False))+int(total>0 and passed==total and not result['staticErrors'])
    elif task['kind']=='D':points=int(bool(diagnostic and diagnostic.get('diagnosisCorrect')))+int(result.get('compiled',False))+int(total>0 and passed==total and not result['staticErrors'])
    else:points=maximum*passed/total if total else 0
    if result['staticErrors']:points=0
    result.update(pointsEarned=round(points,2),maxPoints=maximum,score=round(points/maximum*100))
    if diagnostic and not diagnostic.get('diagnosisCorrect'):
        result['message']=result.get('message','')+' Выбранные категории диагностики требуют пересмотра; балл за диагноз не начислен.'
    if result.get('status') not in ('COMPILE_ERROR','DEPENDENCY_ERROR','BLOCKED','ANALYSIS_REQUIRED','REPAIR_REQUIRED','STATIC_ERROR'):
        result['status']='PASS' if points==maximum and total>0 and passed==total else 'FAIL'
    if result['mode']=='compile':result.update(status='COMPILED' if result.get('compiled') else result['status'],pointsEarned=0,score=0,message='Проверена только компиляция. Баллы за выполнение начисляются после запуска тестов.')
    return result

def grade(task,files,mode='test'):
    folder=DATA/'.build/runs'/('v2-'+uuid.uuid4().hex);folder.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    result=dict(status='FAIL',score=0,pointsEarned=0,maxPoints=task['maxPoints'],mode=mode,tests=[],staticErrors=[],criticalFailures=[],compiled=False,compiler=doctor()['compiler'],codeHash=digest,buildDirectory=str(folder.relative_to(DATA)))
    if not doctor()['available']:result.update(status='BLOCKED',message='Компилятор недоступен.');return finish(task,result)
    if task['kind']=='D' and not latest_diagnosis(task['id']):result.update(status='ANALYSIS_REQUIRED',message='Сначала зафиксируйте словами характер дефекта и затронутые правила.');return finish(task,result)
    for name in ('solution.hpp','solution.cpp',*task.get('starterFiles',{})):
        content=files.get(name,'')
        if name.endswith('.hpp'):content='#pragma once\n'+content
        (folder/name).write_text(content,encoding='utf-8')
    sources=[];dependency_hashes={};missing=[];user_sources='\n'.join(v for name,v in files.items() if name.endswith(('.hpp','.cpp')))
    for task_id in task.get('dependencies',[]):
        dependency=get_task(task_id);values=student_files(dependency)
        if not meaningful(values.get('solution.hpp','')+values.get('solution.cpp','')):missing.append(task_id);continue
        target=folder/('dep-'+task_id);target.mkdir()
        for name in ('solution.hpp','solution.cpp'):
            text=values.get(name,'');(target/name).write_text(('#pragma once\n' if name.endswith('.hpp') else '')+text,encoding='utf-8')
        (folder/NAMES[task_id]).write_text('#pragma once\n#include "dep-'+task_id+'/solution.hpp"\n',encoding='utf-8')
        sources.append(target/'solution.cpp');user_sources+='\n'+values.get('solution.hpp','')+'\n'+values.get('solution.cpp','')
        dependency_hashes[task_id]=hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
    result['dependencyHashes']=dependency_hashes
    if missing:result.update(status='DEPENDENCY_ERROR',message='Нужны ваши исходники: '+', '.join(missing)+'. Готовые решения не подставляются.',missingDependencies=missing);return finish(task,result)
    for name in task.get('fixtures',[]):shutil.copyfile(FIXTURES/(name+'.hpp'),folder/(name+'.hpp'))
    clean=meaningful(user_sources)
    if re.search(r'\b(new|delete)\b|\b(malloc|calloc|realloc|free)\s*\(|\btemplate\s*<',clean):result['staticErrors'].append('День 1: не используйте собственную динамическую память или шаблоны.')
    if re.search(r'\bstd\s*::\s*(vector|deque|list|array|map|set|unordered_map|unordered_set|forward_list)\b',clean):result['staticErrors'].append('Храните данные в собственных фиксированных массивах, без готовых STL-контейнеров.')
    if re.search(r'\b(printf|scanf|fprintf|fscanf)\s*\(|\b(stdin|stdout)\b',clean):result['staticErrors'].append('Используйте потоки C++ для ввода, вывода и диагностики.')
    if task.get('outsideDefinition') and not re.search(r'\bCounter\s*::\s*reset\s*\(',clean):result['staticErrors'].append('Определение reset должно находиться за пределами класса.')
    if result['staticErrors']:result.update(status='STATIC_ERROR',message='Нарушены ограничения учебного контракта.');return finish(task,result)
    (folder/'candidate.hpp').write_text(task.get('prefix','')+'\n#include "solution.hpp"\n'+task.get('suffix',''),encoding='utf-8')
    sources=[folder/'solution.cpp',*sources]
    includes=[folder,ROOT/'tools']
    if task['runner']=='console':return console_grade(task,folder,sources,includes,result,mode)
    executable=folder/('checks.exe' if os.name=='nt' else 'checks')
    if task['kind']=='S':
        probe=compile_cpp([TESTS/f"{task['id']}-types.cpp",*sources],folder/'signature.exe',includes)
        result['signaturePassed']=probe['code']==0;result['signatureDiagnostics']=probe['output'] if probe['code'] else ''
    built=compile_cpp([TESTS/f"{task['id']}.cpp",*sources,ROOT/'tools/memory.cpp'],executable,includes)
    result.update(compilation=built['output'],compileDuration=built['duration'],compiled=built['code']==0)
    if not result['compiled']:result.update(status='COMPILE_ERROR',message='Реальные ошибки компиляции. Тесты не выполнялись.');return finish(task,result)
    if mode=='compile':return finish(task,result)
    if task.get('unsafeStarter') and meaningful(files.get('solution.hpp',''))==meaningful(task['starter']):result.update(status='REPAIR_REQUIRED',message='Исходный небезопасный фрагмент изучается статически. Внесите исправление перед выполнением.');return finish(task,result)
    for index,case in enumerate(task['tests']):
        run=execute(executable,[str(index)])
        row=dict(name=case['name'],category=case['category'],passed=run['code']==0,output=run['output'],duration=run['duration'],timeout=run['timeout'],exitCode=run['code'],critical=case.get('critical',False))
        result['tests'].append(row)
        if not row['passed'] and row['critical']:result['criticalFailures'].append(case['name'])
    count=sum(row['passed'] for row in result['tests'])
    result['message']='Все перечисленные автоматические контракты проверены.' if count==len(result['tests']) else 'Есть непройденные контракты: откройте соответствующие проверки.'
    if task['kind']=='D':result['reviewNote']='Диагностический балл проверяет выбранные правила; свободный разбор сохранён и не оценивается по ключевым словам.'
    return finish(task,result,count,len(result['tests']))

def console_grade(task,folder,sources,includes,result,mode):
    from .console import cases,evaluate
    program=folder/('program.exe' if os.name=='nt' else 'program')
    built=compile_cpp([folder/'main.cpp',*sources],program,includes)
    result.update(compilation=built['output'],compiled=built['code']==0,compileDuration=built['duration'])
    if not result['compiled']:result.update(status='COMPILE_ERROR',message='Программа не собрана.');return finish(task,result)
    if mode=='compile':return finish(task,result)
    for case in cases():
        run=execute(program,stdin_text=case['input'],separate_stderr=True)
        ok,message=evaluate(case,run)
        result['tests'].append(dict(name=case['name'],category=case['category'],passed=ok,output=message+('\nstdout:\n'+run['output'] if run['output'] else '')+('\nstderr:\n'+run.get('stderr','') if run.get('stderr') else ''),duration=run['duration'],timeout=run['timeout'],exitCode=run['code'],critical=case['critical'],weight=case['weight']))
        if not ok and case['critical']:result['criticalFailures'].append(case['name'])
    probe=folder/'scenario_probe.cpp'
    probe.write_text('''#include "candidate.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>
int main(){for(const char* input:{"-1\\n","5\\n"}){std::istringstream in(input);std::ostringstream out;bool caught=false;try{(void)run_stereolab(in,out);}catch(const std::out_of_range&){caught=true;}if(!caught || !out.str().empty())return 1;}return 0;}
''',encoding='utf-8')
    executable=folder/'scenario_probe.exe';check=compile_cpp([probe,*sources],executable,includes)
    run=execute(executable) if check['code']==0 else None
    ok=bool(run and run['code']==0)
    result['tests'].append(dict(name='Функция обработки бросает out_of_range для N вне 0..4',category='exception',passed=ok,output='' if ok else 'run_stereolab должен бросить out_of_range до публикации отчёта. '+check['output'],duration=(run or {}).get('duration',0),timeout=(run or {}).get('timeout',False),critical=True,weight=2))
    if not ok:result['criticalFailures'].append('Неверный контракт исключения при недопустимом N')
    passed=sum(t.get('weight',1) for t in result['tests'] if t['passed']);total=sum(t.get('weight',1) for t in result['tests'])
    return finish(task,result,passed,total)
