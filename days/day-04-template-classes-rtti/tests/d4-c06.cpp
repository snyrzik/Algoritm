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
TextStack<char*> s; char a[]="hello"; CHECK(s.Push(a)); a[0]=char(88); CHECK(std::strcmp(s.Get(),"hello")==0);
}
void test_1() {
TextStack<char*> a; a.Push("one"); a.Push("two"); auto b=a; CHECK(b.Pop()); CHECK(std::strcmp(b.Get(),"one")==0 && std::strcmp(a.Get(),"two")==0);
}
void test_2() {
TextStack<char*> s; CHECK(s.Empty() && s.Count()==0 && !s.Pop()); expect_throw<std::out_of_range>([&]{s.Get();}); expect_throw<std::invalid_argument>([&]{s.Push(nullptr);}); CHECK(s.Count()==0);
}
void test_3() {
TextStack<char*> a,b; a.Push("alive"); b=a; a.Pop(); b=mastery_alias(b); CHECK(std::strcmp(b.Get(),"alive")==0);
}
void test_4() {
for(int i=0;i<40;++i){TextStack<char*> s; s.Push(""); CHECK(s.Get()[0]==0); s.Push("owned");}
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
