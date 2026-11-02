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
const int a[]={3,5,9}; CHECK(checked_access(a,3,0)==3 && checked_access(a,3,2)==9);
}
void test_1() {
const int a[]={3}; expect_throw<std::out_of_range>([&]{checked_access(a,0,0);}); expect_throw<std::out_of_range>([&]{checked_access(a,1,1);});
}
void test_2() {
expect_throw<std::invalid_argument>([]{checked_access(nullptr,0,0);}); expect_throw<std::invalid_argument>([]{checked_access(nullptr,5,0);});
}
void test_3() {
int a[]={2}; expect_throw<std::out_of_range>([&]{checked_access(a,1,std::numeric_limits<std::size_t>::max());});
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
