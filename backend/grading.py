import hashlib
import json
import re
import shutil
import uuid
from pathlib import Path
from .catalog import ROOT, DATA
from .compiler import compile_cpp, execute, doctor

def revision(files):
    return hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def static_review(task, files):
    source='\n'.join(v for k,v in files.items() if k.endswith(('.hpp','.cpp')))
    # Checks are limited to explicit exercise constraints, not stylistic grading.
    clean=re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"', '', source, flags=re.S)
    errors=[]
    rules=task.get('staticChecks', [])
    if 'no_containers' in rules and re.search(r'\bstd\s*::\s*(vector|deque|list|array|map|set|unordered_map|unordered_set|forward_list)\b',clean):
        errors.append('Запрещено хранение в готовом STL-контейнере: нужен собственный массив или список.')
    if 'no_rtti' in rules and re.search(r'\b(typeid|dynamic_cast)\b',clean):
        errors.append('В этой задаче выбор поведения через RTTI запрещён.')
    count=len(re.findall(r'\b\w+\s*<[^;{}]+>\s*::\s*~?\w+\s*\(',clean))
    if 'external_methods' in rules and count<1: errors.append('Нужны определения методов за пределами класса.')
    if 'three_external_methods' in rules and count<3: errors.append('Определите не менее трёх методов шаблонного класса вне объявления.')
    if 'no_vararg_pointer_trick' in rules and re.search(r'&\s*count\s*\+\s*1',clean): errors.append('Арифметика &count + 1 непереносима; используйте cstdarg.')
    return errors

def grade(task, files, mode='test'):
    if task.get('version') == 2:
        from .day01_v2.grading import grade as grade_v2
        return grade_v2(task, files, mode)
    folder=DATA/'.build'/'runs'/uuid.uuid4().hex
    folder.mkdir(parents=True,exist_ok=True)
    for name in ('solution.hpp','solution.cpp',*task.get('starterFiles',{})):
        (folder/name).write_text(files.get(name,''),encoding='utf-8')
    wrapper=task.get('prefix','')+'\n#include "solution.hpp"\n'+task.get('suffix','')
    (folder/'candidate.hpp').write_text(wrapper,encoding='utf-8')
    d=doctor()
    memory=bool(task.get('memory'))
    sanitizer=memory and d['addressSanitizer']
    static=static_review(task,files)
    result={'status':'FAIL','score':0,'mode':mode,'tests':[],'staticErrors':static,'memory':{'required':memory,'addressSanitizer':sanitizer,'undefinedSanitizer':sanitizer and d['undefinedSanitizer'],'leakSanitizer':sanitizer and d['leakSanitizer'],'allocationTracking':True},'compiler':d['compiler'],'buildDirectory':str(folder.relative_to(DATA)), 'codeHash':revision(files)}
    if task.get('unsafeStarter') and not sanitizer and files.get('solution.hpp')==task.get('starter'):
        result.update(status='BLOCKED',message='Исходный небезопасный фрагмент не запускается: AddressSanitizer недоступен. Изучите его статически или настройте ASan.')
        return result
    if not d['available']:
        result.update(status='BLOCKED',message='Компилятор недоступен. Откройте диагностику окружения.',compilation=d['details'])
        return result
    test_path=Path(task['_path'])
    day_folder=next(p for p in test_path.parents if p.name.startswith('day-'))
    harness=day_folder/'tests'/f"{task['id']}.cpp"
    exe=folder/'checks.exe' if __import__('os').name=='nt' else folder/'checks'
    sources=[harness,folder/'solution.cpp',ROOT/'tools'/'memory.cpp']
    compiled=compile_cpp(sources,exe,includes=[folder,ROOT/'tools'],sanitize=sanitizer)
    result['compilation']=compiled['output']
    result['compileDuration']=compiled['duration']
    result['compiled']=compiled['code']==0
    if not result['compiled']:
        result.update(status='COMPILE_ERROR',message='Компиляция завершилась ошибкой. Функциональные тесты не запускались.')
        return result
    if mode=='compile':
        result.update(status='COMPILED',message='Компиляция успешна. Корректность поведения ещё не проверена.')
        return result
    for i,test in enumerate(task['tests']):
        run=execute(exe,[str(i)])
        result['tests'].append({'name':test['name'],'category':test['category'],'passed':run['code']==0,'output':run['output'],'duration':run['duration'],'timeout':run['timeout'],'exitCode':run['code']})
    passed=sum(t['passed'] for t in result['tests'])
    result['score']=round(100*passed/len(result['tests'])) if result['tests'] else 0
    ok=passed==len(result['tests']) and not static
    # ASan + instrumented new/delete provide meaningful local evidence. LSan and
    # UBSan availability are reported independently, never silently invented.
    result['status']='PASS' if ok and (not memory or sanitizer) else 'UNVERIFIED' if ok else 'FAIL'
    result['message']='Все обязательные автоматические проверки прошли.' if result['status']=='PASS' else 'Проверки поведения прошли; память не подтверждена ASan.' if ok else 'Есть непройденные обязательные проверки.'
    if task['kind']=='D':
        result['reviewNote']='Объяснение в notes.md сохранено для самостоятельного разбора. Его смысл и читаемость кода автоматически не оцениваются.'
        if len(files.get('notes.md','').strip())<20:
            result['status']='REVIEW_REQUIRED' if ok else result['status']
            result['message']+=' Добавьте объяснение причины в notes.md.'
    return result

def grade_answer(task, answer):
    if not isinstance(answer,list) or any(type(x) is not int or x<0 or x>=len(task['options']) for x in answer):
        raise ValueError('Некорректный список ответов')
    if not answer: raise ValueError('Выберите ответ')
    ok=sorted(set(answer))==sorted(task['answer'])
    return {'status':'PASS' if ok else 'FAIL','score':100 if ok else 0,'answer':answer,'mode':'answer','message':'Ответ верный.' if ok else 'Ответ не соответствует контракту C++17.'}
