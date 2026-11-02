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
BadText a("abc"); BadText b(a); b[0]=char(120); CHECK(std::strcmp(a.c_str(),"abc")==0);
}
void test_1() {
BadText a("old"); {BadText b("new"); CHECK(&(a=b)==&a);} a=mastery_alias(a); CHECK(std::strcmp(a.c_str(),"new")==0);
}
void test_2() {
BadText a(""); CHECK(a.c_str()[0]==0); expect_throw<std::out_of_range>([&]{(void)a[0];});
}
void test_3() {
expect_throw<std::invalid_argument>([]{BadText a(nullptr);}); BadText a("a"); expect_throw<std::out_of_range>([&]{(void)a[1];});
}
void test_4() {
for(int i=0;i<100;++i){BadText a("longer text"); BadText b=a; CHECK(std::strcmp(b.c_str(),"longer text")==0);}
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
