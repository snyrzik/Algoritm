"""Ready-to-copy C++ mains and learner-reported results. Never runs a compiler."""
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from .catalog import ROOT,get_task,student_files
from .answers import revision

COMPLETED={'PASS','SELF_CHECKED'}
HEADERS='''#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <stdexcept>
#include <type_traits>
#include <limits>
#include <utility>
#include <cstddef>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <cstdarg>
#include <new>
#include <typeinfo>
#include <algorithm>
'''

def require_program(task):
    if task['kind'] not in ('S','D','C'):raise ValueError('Самопроверка с main доступна для программных заданий')

def cpp_string(value):return json.dumps(value,ensure_ascii=True)

def main_source(task):
    require_program(task)
    if task.get('localMain'):
        from .theory import project_guide
        return project_guide(task)['main']
    checks_text=task.get('checks','')+'\n'.join(case['code'] for case in task.get('tests',[]))
    needs_memory=bool(task.get('memory')) or 'mastery_memory' in checks_text
    support='''template<class T> T& mastery_alias(T& value) { return value; }
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(std::string("CHECK failed: ") + #__VA_ARGS__); } while (false)
'''
    if 'expect_throw' in checks_text:
        support+='''template<class E,class F> void expect_throw(F&& fn) {
    bool caught=false; try { fn(); } catch(const E&) { caught=true; } CHECK(caught);
}
'''
    if 'Tracked' in checks_text:
        support+='struct Tracked'+(ROOT/'tools/support.hpp').read_text(encoding='utf-8').split('struct Tracked',1)[1]
    memory=(ROOT/'tools/memory.cpp').read_text(encoding='utf-8') if needs_memory else ''
    # All checking helpers are in this file. No support library or sanitizer setup.
    pre=HEADERS+'\n'+memory+'\n'+support+'\n'
    pre+='inline bool close_value(double a,double b,double eps=1e-9){return std::abs(a-b)<=eps;}\n'
    pre+='inline void require_contract(bool ok,const char* contract){if(!ok)throw std::runtime_error(contract);}\n'
    pre+=task.get('prefix','')+'\n#include "solution.hpp"\n'+task.get('suffix','')+'\n'
    pre+=task.get('checks','')+'\nnamespace mastery_checks {\n'
    for i,case in enumerate(task.get('tests',[])):
        source=re.sub(r'\b(\w+)\s*=\s*\1\s*;',r'\1=mastery_alias(\1);',case['code'])
        source=re.sub(r'\b(\w+)\s*=\s*std::move\(\1\);',r'\1=std::move(mastery_alias(\1));',source)
        pre+=f'void case_{i+1}() {{\n{source}\n}}\n'
    pre+='}\n\nint main() {\n'
    pre+='''    // Warm the standard stream facets before checking allocation balance.
    { std::ostringstream out; out << std::setprecision(3) << 1.25;
      std::istringstream in("1.25 2"); double d=0; int n=0; in >> d >> n; }
    int failed=0;
'''
    for i,_ in enumerate(task.get('tests',[])):
        label=f'case-{i+1:02}'
        pre+='''    {
        const auto before=mastery_memory::live;
        auto* original=std::cout.rdbuf();
        try {
            { std::ostringstream captured; std::cout.rdbuf(captured.rdbuf());
'''+f'              mastery_checks::case_{i+1}();\n'+'''              std::cout.rdbuf(original); }
            mastery_memory::fail_after=-1;
            CHECK(mastery_memory::live==before);
'''+f'            std::cout << "{label}: OK\\n";\n'+'''        } catch (const std::exception& error) {
            std::cout.rdbuf(original); mastery_memory::fail_after=-1; ++failed;
'''+f'            std::cout << "{label}: FAIL: " << error.what() << "\\n";\n'+'''        } catch (...) {
            std::cout.rdbuf(original); mastery_memory::fail_after=-1; ++failed;
'''+f'            std::cout << "{label}: FAIL: unexpected exception\\n";\n'+'''        }
    }
'''
    pre+=f'    if(failed==0)std::cout << "ALL CHECKS PASSED ({len(task.get("tests",[]))})\\n";\n'
    if not needs_memory:
        pre=pre.replace('        const auto before=mastery_memory::live;\n','').replace('mastery_memory::fail_after=-1;','').replace('            CHECK(mastery_memory::live==before);\n','')
    return '// main.cpp: your implementation belongs in solution.hpp / solution.cpp.\n'+pre+'    return failed==0 ? 0 : 1;\n}\n'

def guide(task):
    require_program(task)
    if task.get('localMain'):
        from .theory import project_guide
        return project_guide(task)
    cases=[dict(id=f'case-{i:02}',name=t['name'],category=t['category'],critical=t.get('critical',False)) for i,t in enumerate(task.get('tests',[]),1)]
    main=main_source(task)
    extra=[]
    for name,source in task.get('starterFiles',{}).items():
        if name.endswith('.hpp'):extra.append(dict(name=name,source=source))
    dependencies=[]
    expected=''.join(c['id']+': OK\n' for c in cases)+f'ALL CHECKS PASSED ({len(cases)})\n' if task.get('runner')!='console' else ''
    return dict(task=task['id'],mode='self-check',main=main,originalCode=task.get('starter','') if task['kind']=='D' else '',expectedOutput=expected,cases=cases,console=task.get('runner')=='console',extraFiles=extra,dependencies=dependencies,guideHash=hashlib.sha256(main.encode()).hexdigest(),instructions='Добавьте main.cpp к своему проекту C++17 рядом с solution.hpp и solution.cpp. Если удобнее писать всё в одном файле, замените строку #include "solution.hpp" своим решением. В архиве проверки уже собраны все ваши файлы и необходимые заголовки.',review=['Проверьте все перечисленные обычные, граничные и ошибочные случаи.','Сравните вывод с ожидаемым; для вещественных чисел учитывайте допуск из условия.','После совпадения отметьте результат самостоятельно. Сайт не запускает ваш код.'])

def report(task,body,files):
    require_program(task)
    complete=body.get('completed')
    if type(complete) is not bool:raise ValueError('Укажите, совпал ли результат проверки')
    current=guide(task)
    checked=body.get('checkedCases',[])
    allowed={c['id'] for c in current['cases']}
    if not isinstance(checked,list) or any(not isinstance(x,str) or x not in allowed for x in checked):raise ValueError('Неизвестные случаи проверки')
    if complete and set(checked)!=allowed:raise ValueError('Подтвердите проверку всех случаев')
    maximum=task.get('maxPoints',0)
    return dict(status='SELF_CHECKED' if complete else 'NEEDS_WORK',mode='self-check',score=100 if complete else 0,pointsEarned=maximum if complete else 0,maxPoints=maximum,manual=True,checkedCases=checked,guideHash=current['guideHash'],codeHash=revision(files),message='Вы отметили, что все результаты совпали. Самопроверка сохранена.' if complete else 'Вы отметили расхождения. Задание снова ожидает проверки.')

def bundle(task):
    current=guide(task);files=student_files(task);content={name:value for name,value in files.items() if name.endswith(('.hpp','.cpp')) and name!='main.cpp'}
    for item in current['extraFiles']:content.setdefault(item['name'],item['source'])
    for dependency in current['dependencies']:
        values=student_files(get_task(dependency['id']));folder='dependencies/'+dependency['id']
        for name,value in values.items():
            if name in ('solution.hpp','solution.cpp'):
                # Unique source names also work in IDEs that place all .obj files
                # in one directory (several solution.cpp files would collide).
                target=dependency['id']+'.cpp' if name=='solution.cpp' else name
                content[folder+'/'+target]=('#pragma once\n' if name.endswith('.hpp') else '')+value
        content[dependency['name']]='#pragma once\n#include "'+folder+'/solution.hpp"\n'
    content['main.cpp']=current['main']
    content['expected.txt']=current['expectedOutput'] if not current['console'] else '\n'.join(c['name']+'\nINPUT:\n'+c['input']+'STDOUT:\n'+c['expectedOutput']+'STDERR:\n'+c['expectedError'] for c in current['cases'])
    content['README.txt']='C++17. Add main.cpp and all solution.cpp files to your IDE project.\nKeep the header directory structure.\nCompare the output with expected.txt; mark the result on the site.\n'
    if task.get('localMain'):
        from .theory import LECTURE
        content['README.md']=(LECTURE/'local-checks/README.md').read_text(encoding='utf-8')
        content.pop('README.txt')
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,value in content.items():archive.writestr(name,value)
    return output.getvalue()
