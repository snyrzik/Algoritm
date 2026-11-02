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
CHECK(std::is_abstract_v<AbstractStack<int>>); CHECK(std::has_virtual_destructor_v<AbstractStack<int>>);
}
void test_1() {
SingleStack<int> s; AbstractStack<int>& b=s; CHECK(b.Empty()); CHECK(b.Push(7) && b.Full()); CHECK(!b.Push(8)); int out=0; CHECK(b.Get(out) && out==7); CHECK(b.Pop(out) && out==7 && b.Empty());
}
void test_2() {
AbstractStack<std::string>* s=new SingleStack<std::string>(); s->Push("owned"); std::string out; CHECK(s->Pop(out) && out=="owned"); delete s;
}
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    try {
        const auto live_before = mastery_memory::live;
        switch (std::stoi(argv[1])) {
case 0: test_0(); break;
case 1: test_1(); break;
case 2: test_2(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
