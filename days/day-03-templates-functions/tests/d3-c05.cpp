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
int a[]={1,3,4},b[]={4,3,1}; CHECK(index_of_min(a,3)==0 && index_of_min(b,3)==2);
}
void test_1() {
int a[]={3,1,1,2}; CHECK(index_of_min(a,4)==1); double b[]={2.5}; CHECK(index_of_min(b,1)==0);
}
void test_2() {
int a[]={1}; expect_throw<std::invalid_argument>([&]{index_of_min(a,0);}); expect_throw<std::invalid_argument>([]{index_of_min<int>(nullptr,1);});
}
void test_3() {
std::string a[]={"z","az","ba"}; CHECK(index_of_min(a,3)==1);
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
