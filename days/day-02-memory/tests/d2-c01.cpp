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
char* p=concat_copy("ab","cd"); CHECK(std::strcmp(p,"abcd")==0); delete[] p; p=concat_copy("",""); CHECK(p[0]==0); delete[] p;
}
void test_1() {
CHECK(compare_text("az","ba")<0 && compare_text("a","a")==0 && compare_text("z","a")>0);
}
void test_2() {
int a[]={1,2,3},b[3]{}; copy_ints(b,a,3); CHECK(b[0]==1 && b[2]==3); copy_ints(nullptr,nullptr,0);
}
void test_3() {
char a[]="abcdef"; shift_left(a,2); CHECK(std::strcmp(a,"cdef")==0); shift_left(a,4); CHECK(a[0]==0); shift_left(a,0);
}
void test_4() {
expect_throw<std::invalid_argument>([]{concat_copy(nullptr,"");}); expect_throw<std::invalid_argument>([]{compare_text("",nullptr);}); expect_throw<std::invalid_argument>([]{copy_ints(nullptr,nullptr,1);}); char a[]="a"; expect_throw<std::out_of_range>([&]{shift_left(a,2);}); CHECK(a[0]==char(97));
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
