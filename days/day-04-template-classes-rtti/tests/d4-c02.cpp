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
FixedBuffer<int,3> a; CHECK(a.capacity()==3 && a[0]==0 && a[2]==0); CHECK(FixedBuffer<double>().capacity()==256);
}
void test_1() {
FixedBuffer<int,2> a; a[1]=8; const auto& b=a; CHECK(b[1]==8);
}
void test_2() {
FixedBuffer<int,1> a; const auto& b=a; expect_throw<std::out_of_range>([&]{(void)a[1];}); expect_throw<std::out_of_range>([&]{(void)b[1];});
}
void test_3() {
FixedBuffer<std::string,2> a; a[0]="ok"; auto b=a; b[0]="other"; CHECK(a[0]=="ok");
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
