from contextlib import contextmanager
from pathlib import Path
from backend.catalog import ROOT,DATA,get_task,student_files,student_dir

FIXTURES=ROOT/'tests/fixtures/day01_v2'
def reference_files(task_id):
    task=get_task(task_id);number=task['number'];group=task['group'];label=group+str(number)
    files={'solution.hpp':(FIXTURES/(label+'.hpp')).read_text(encoding='utf-8'),'solution.cpp':'','notes.md':'Test infrastructure only.'}
    if group=='C':files.update({'solution.cpp':(FIXTURES/'C1.cpp').read_text(encoding='utf-8'),'main.cpp':(FIXTURES/'main.cpp').read_text(encoding='utf-8')})
    return files

@contextmanager
def seeded_components():
    # DATA belongs to the test suite's TemporaryDirectory, never the real user.
    if DATA==ROOT:raise AssertionError('Reference implementations may not enter the learner profile')
    backup={}
    try:
        for label in ('a01','a02','a03','b01','b02'):
            task=get_task('d01-v2-'+label);folder=student_dir(task);values=reference_files(task['id'])
            for name,text in values.items():
                path=folder/name;backup[path]=path.read_bytes() if path.exists() else None;path.write_text(text,encoding='utf-8')
        yield
    finally:
        for path,value in backup.items():
            if value is None:path.unlink(missing_ok=True)
            else:path.write_bytes(value)

S_REFERENCES={
1:'class Score{int value_;public:explicit Score(int v):value_(v){}int value()const{return value_;}};',
2:'void increase_by(Score& value,int n){value.add(n);}',
3:'Score operator+(const Score& b)const{return Score(value_+b.value_);}',
4:'Score& operator+=(const Score& b){value_+=b.value_;return *this;}',
5:'Score operator*(double k,const Score& value){return value*k;}',
6:'bool operator==(const Score& b)const{return value_==b.value_;}',
7:'friend std::ostream& operator<<(std::ostream& out,const Score& value){return out<<value.value_;}',
8:'int& operator[](std::size_t i){if(i>=3)throw std::out_of_range("index");return data_[i];}',
9:'const int& operator[](std::size_t i)const{if(i>=3)throw std::out_of_range("index");return data_[i];}',
10:'double operator()(double x)const{return a_*x*x+b_*x+c_;}',
11:'Counter& operator++(){++value_;return *this;}',
12:'Counter operator++(int){Counter old=*this;++(*this);return old;}',
13:'class Counter{int value_;public:explicit Counter(int n):value_(n){}int value()const{return value_;}void reset(int);};void Counter::reset(int n){value_=n;}',
14:'std::istream& operator>>(std::istream& in,Point& value){char p=0,c=0,q=0;int x=0,y=0;if(in>>p>>x>>c>>y>>q){if(p==char(40)&&c==char(44)&&q==char(41))value=Point{x,y};else in.setstate(std::ios::failbit);}return in;}',
}
def debug_reference(task):
    source=task['starter'];n=task['number']
    if n==1:return source.replace('Score& operator+','Score operator+')
    if n==2:return source.replace('Meter operator+=','Meter& operator+=')
    if n==3:return '#include <stdexcept>\nstruct Triple{int data[3]={1,2,3};int& operator[](int i){if(i<0||i>=3)throw std::out_of_range("index");return data[i];}const int& operator[](int i)const{if(i<0||i>=3)throw std::out_of_range("index");return data[i];}};'
    if n==4:return source.replace('std::ostream operator<<','std::ostream& operator<<')
    if n==5:return '#include <istream>\nstruct Duo{int first,second;};std::istream& operator>>(std::istream& in,Duo& d){int a=0,b=0;char c=0;if(in>>a>>c>>b){if(c==char(44))d=Duo{a,b};else in.setstate(std::ios::failbit);}return in;}'
    return '#include <cmath>\nstruct Measurement{double x;explicit Measurement(double v):x(v){}bool operator==(const Measurement& b)const{return std::abs(x-b.x)<=1e-9;}bool operator!=(const Measurement& b)const{return !(*this==b);}};'
