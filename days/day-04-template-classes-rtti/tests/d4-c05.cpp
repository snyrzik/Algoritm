#include "candidate.hpp"
#include <cstddef>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <sstream>
#include <string>
#include <stdexcept>
#include <type_traits>
#include <limits>
#include <utility>
#include <typeinfo>
#include <complex>
#include "support.hpp"

void test_0() {
DynamicStack<int> s; int v=91; CHECK(s.Empty() && s.Count()==0 && !s.Get(v) && !s.Pop(v) && v==91);
}
void test_1() {
DynamicStack<int> s; CHECK(s.Push(4)); CHECK(s.Push(7)); const auto& c=s; int v=0; CHECK(c.Get(v) && v==7 && s.Count()==2); CHECK(s.Pop(v) && v==7); CHECK(s.Pop(v) && v==4); CHECK(s.Empty());
}
void test_2() {
DynamicStack<int> s; int out=0; for(int i=0;i<20;++i){CHECK(s.Push(i)); CHECK(s.Pop(out) && out==i);} CHECK(s.Count()==0);
}
void test_3() {
DynamicStack<int> a; a.Push(1); a.Push(2); DynamicStack<int> b(a); int out=0; CHECK(b.Pop(out) && out==2); CHECK(a.Count()==2); DynamicStack<int> c; c=b; c=mastery_alias(c); CHECK(c.Pop(out) && out==1);
}
void test_4() {
const int before=Tracked::alive; {DynamicStack<Tracked> s; Tracked v(4); s.Push(v); s.Push(v); DynamicStack<Tracked> copy(s); CHECK(copy.Count()==2);} CHECK(Tracked::alive==before);
}
void test_5() {
DynamicStack<Tracked> s; Tracked v(4); Tracked::copies_before_throw=0; bool caught=false; try{s.Push(v);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && s.Count()==0);
}
void test_6() {
DynamicStack<Tracked> s; Tracked a(1),b(2); s.Push(a); s.Push(b); const int live=Tracked::alive; Tracked::copies_before_throw=1; bool caught=false; try{DynamicStack<Tracked> copy(s);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && Tracked::alive==live && s.Count()==2);
}
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    try {
        const auto live_before = mastery_memory::live;
        switch (std::stoi(argv[1])) {
case 0: test_0(); break;
case 1: test_1(); break;
case 2: test_2(); break;
case 3: test_3(); break;
case 4: test_4(); break;
case 5: test_5(); break;
case 6: test_6(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
