"""Optional developer syntax audit of the seven supplied mains using API declarations only."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.cpp_toolchain import toolchain,run_process
from backend.lectures import SOURCE

DECLARATIONS={
 'CMyString.h':'''#pragma once
#include <cstddef>
class CMyString {public: CMyString(); explicit CMyString(const char*); CMyString(const CMyString&); CMyString& operator=(const CMyString&); ~CMyString(); std::size_t size()const; const char* c_str()const; void erase(std::size_t,std::size_t); void replace_range(std::size_t,std::size_t,const char*);};
''',
 'DynamicVector.h':'''#pragma once
#include <cstddef>
class DynamicVector {public: DynamicVector(std::size_t,double=0.0); DynamicVector(const DynamicVector&); DynamicVector& operator=(const DynamicVector&); ~DynamicVector(); std::size_t size()const; double& operator[](std::size_t); const double& operator[](std::size_t)const; void resize(std::size_t,double=0.0); void insert(std::size_t,double); void erase(std::size_t);};
''',
 'GenericAlgorithms.h':'''#pragma once
#include <cstddef>
template<typename T> T maximum(T,T);
template<> const char* maximum<const char*>(const char*,const char*);
template<typename T> void swap_values(T&,T&);
template<typename T> T minimum_of_three(T,T,T);
template<typename T> std::size_t index_of_min(const T*,std::size_t);
const char* minimum_value(const char*,const char*);
''',
 'IStack.h':'''#pragma once
#include <cstddef>
template<typename T> class IStack {public: virtual ~IStack()=default; virtual bool push(const T&)=0; virtual bool pop(T&)=0; virtual bool peek(T&)const=0; virtual std::size_t size()const=0;};
''',
 'FixedStack.h':'''#pragma once
#include "IStack.h"
template<typename T,int Capacity=256> class FixedStack:public IStack<T> {public: FixedStack(); bool push(const T&)override; bool pop(T&)override; bool peek(T&)const override; std::size_t size()const override; bool empty()const; bool full()const;};
''',
 'LinkedStack.h':'''#pragma once
#include "IStack.h"
template<typename T> class LinkedStack:public IStack<T> {public: LinkedStack(); LinkedStack(const LinkedStack&); LinkedStack& operator=(const LinkedStack&); ~LinkedStack()override; bool push(const T&)override; bool pop(T&)override; bool peek(T&)const override; std::size_t size()const override;};
''',
 'PostfixEvaluator.h':'''#pragma once
#include <string>
double evaluate_postfix(const std::string&);
''',
 'RttiLab.h':'''#pragma once
class Shape {public: virtual ~Shape()=default; virtual double area()const=0;};
class Rectangle:public Shape {public: Rectangle(double,double); double area()const override;};
class Circle:public Shape {public: explicit Circle(double); double area()const override;};
bool is_rectangle(const Shape&); const Rectangle& require_rectangle(const Shape&); bool is_exact_circle(const Shape&);
'''
}

def main():
    tc=toolchain()
    if not tc['exe']:raise SystemExit('Optional syntax audit needs a C++17 compiler; the site does not.')
    with tempfile.TemporaryDirectory(prefix='mastery-lecture-pack-api-') as temp:
        folder=Path(temp)
        for name,text in DECLARATIONS.items():(folder/name).write_text(text,encoding='utf-8')
        from tools.prepare_lecture04 import SOURCE as FOURTH
        import re
        instructions=(FOURTH/'CODEX_INSTRUCTIONS.md').read_text(encoding='utf-8')
        contracts=re.findall(r'```cpp\n(.*?)\n```',instructions,re.S)
        for name,contract in zip(('forward_chain.hpp','bidirectional_list.hpp','collection_operations.hpp'),contracts,strict=True):
            (folder/name).write_text(contract,encoding='utf-8')
        count=0
        for source in sorted([*SOURCE.glob('lecture-*/MAIN_*.cpp'),*FOURTH.glob('MAIN_*.cpp')]):
            args=[tc['exe'],'/nologo','/std:c++17','/EHsc','/utf-8','/W4','/Zs',f'/I{folder}',source] if tc['kind']=='msvc' else [tc['exe'],'-std=c++17','-Wall','-Wextra','-Wconversion','-Wpedantic','-fsyntax-only','-I',folder,source]
            value=run_process(args,folder,tc['env'],30)
            if value['code']:raise AssertionError((source.name,value['output']))
            count+=1
    print(f'{count} supplied mains passed syntax/API checks. No solution implementations or learner code were executed.')

if __name__=='__main__':main()
