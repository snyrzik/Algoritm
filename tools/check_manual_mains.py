"""Optional developer syntax audit. It never reads or compiles learner code."""
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,catalog
from backend.self_check import guide
from backend.compiler import toolchain,run_process

PROJECT_CONTRACTS={
 'Matrix2x2.hpp':'''#pragma once
#include <cstddef>
#include <iosfwd>
class Matrix2x2 {public: Matrix2x2(); Matrix2x2(double,double,double,double); double& operator()(std::size_t,std::size_t); double operator()(std::size_t,std::size_t) const; Matrix2x2& operator+=(const Matrix2x2&);};
Matrix2x2 operator+(const Matrix2x2&,const Matrix2x2&); Matrix2x2 operator-(const Matrix2x2&,const Matrix2x2&); Matrix2x2 operator-(const Matrix2x2&); Matrix2x2 operator*(const Matrix2x2&,const Matrix2x2&); Matrix2x2 operator*(const Matrix2x2&,double); Matrix2x2 operator*(double,const Matrix2x2&); bool operator==(const Matrix2x2&,const Matrix2x2&); bool operator!=(const Matrix2x2&,const Matrix2x2&); std::ostream& operator<<(std::ostream&,const Matrix2x2&); std::istream& operator>>(std::istream&,Matrix2x2&);
''',
 'Point2D.hpp':'''#pragma once
#include "Matrix2x2.hpp"
struct Point2D {double x; double y;}; Point2D transform(const Matrix2x2&,const Point2D&);
''',
 'CMyString.hpp':'''#pragma once
#include <cstddef>
#include <initializer_list>
#include <iosfwd>
class CMyString {public: CMyString(); CMyString(const char*); CMyString(const CMyString&); CMyString& operator=(const CMyString&); ~CMyString(); std::size_t size()const; const char* c_str()const; char& operator[](std::size_t); char operator[](std::size_t)const; CMyString& operator+=(const CMyString&); CMyString operator()(std::initializer_list<std::size_t>)const;};
bool operator==(const CMyString&,const CMyString&); bool operator!=(const CMyString&,const CMyString&); CMyString operator+(const CMyString&,const CMyString&); CMyString operator!(const CMyString&); CMyString operator^(const CMyString&,std::size_t); std::ostream& operator<<(std::ostream&,const CMyString&); std::istream& operator>>(std::istream&,CMyString&);
''',
 'DynamicVector.hpp':'''#pragma once
#include <cstddef>
#include <iosfwd>
class DynamicVector {public: DynamicVector(std::size_t,double=0); DynamicVector(const DynamicVector&); DynamicVector& operator=(const DynamicVector&); ~DynamicVector(); std::size_t size()const; double& operator[](std::size_t); double operator[](std::size_t)const; DynamicVector& operator+=(const DynamicVector&);};
DynamicVector operator+(const DynamicVector&,const DynamicVector&); DynamicVector operator-(const DynamicVector&,const DynamicVector&); double operator*(const DynamicVector&,const DynamicVector&); DynamicVector operator*(const DynamicVector&,double); DynamicVector operator*(double,const DynamicVector&); DynamicVector operator/(const DynamicVector&,double); bool operator==(const DynamicVector&,const DynamicVector&); bool operator!=(const DynamicVector&,const DynamicVector&); std::ostream& operator<<(std::ostream&,const DynamicVector&); double triangle_area(const DynamicVector&,const DynamicVector&);
''',
}

def main():
    tc=toolchain()
    if not tc['exe']:raise SystemExit('Optional syntax audit needs a local C++17 compiler. The app does not.')
    theory=json.loads((ROOT/'tests/lecture01_contracts.json').read_text(encoding='utf-8'))
    count=0
    with tempfile.TemporaryDirectory(prefix='mastery-main-audit-') as temp:
        for task in catalog(True):
            if task['kind']!='C' and task['id']!='l01-v3-c04':continue
            folder=Path(temp)/task['id'];folder.mkdir()
            current=guide(task)
            (folder/'main.cpp').write_text(current['main'],encoding='utf-8')
            for name,source in PROJECT_CONTRACTS.items():(folder/name).write_text(source,encoding='utf-8')
            source=theory[str(task['chapter'])] if task.get('section')=='lecture-theory' else '#include "contracts.hpp"\n'
            (folder/'solution.hpp').write_text('#include <cstddef>\n#include <iosfwd>\n'+source,encoding='utf-8')
            (folder/'support.hpp').write_text('#pragma once\n',encoding='utf-8')
            for item in current['extraFiles']:(folder/item['name']).write_text(item['source'],encoding='utf-8')
            includes=[folder,ROOT/'tests',ROOT/'tools']
            args=[tc['exe'],'/nologo','/std:c++17','/EHsc','/W4','/utf-8','/Zs',*[f'/I{p}' for p in includes],folder/'main.cpp'] if tc['kind']=='msvc' else [tc['exe'],'-std=c++17','-Wall','-Wextra','-Wconversion','-Wpedantic','-fsyntax-only',*[f'-I{p}' for p in includes],folder/'main.cpp']
            value=run_process(args,folder,tc['env'],30)
            if value['code']:raise AssertionError((task['id'],value['output']))
            count+=1
    print(f'{count} ready mains: syntax/API declarations passed. No learner implementation was executed.')

if __name__=='__main__':main()
