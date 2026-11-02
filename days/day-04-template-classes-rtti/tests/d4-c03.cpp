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
TFixedStack<int,3> s; int v=91; CHECK(s.Empty() && s.Count()==0 && !s.Get(v) && !s.Pop(v) && v==91);
}
void test_1() {
TFixedStack<int,3> s; CHECK(s.Push(4)); CHECK(s.Push(7)); const auto& c=s; int v=0; CHECK(c.Get(v) && v==7 && s.Count()==2); CHECK(s.Pop(v) && v==7); CHECK(s.Pop(v) && v==4); CHECK(s.Empty());
}
void test_2() {
TFixedStack<int,3> s; int out=0; for(int i=0;i<20;++i){CHECK(s.Push(i)); CHECK(s.Pop(out) && out==i);} CHECK(s.Count()==0);
}
void test_3() {
TFixedStack<int,2> s; CHECK(s.Push(1) && s.Push(2) && s.Full()); CHECK(!s.Push(3) && s.Count()==2); int out=0; CHECK(s.Pop(out) && out==2 && !s.Full());
}
void test_4() {
TFixedStack<std::string,3> a; a.Push("a"); auto b=a; b.Push("b"); std::string out; CHECK(a.Get(out) && out=="a"); CHECK(b.Pop(out) && out=="b");
}
void test_5() {
TFixedStack<Tracked,3> s; Tracked v(7); Tracked::copies_before_throw=0; bool caught=false; try{s.Push(v);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && s.Count()==0);
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
