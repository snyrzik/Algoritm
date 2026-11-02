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
Matrix2x2 m(1,2,3,4); m(1,0)=7; const auto& c=m; CHECK(c(0,1)==2 && c(1,0)==7); CHECK(Matrix2x2()==Matrix2x2(0,0,0,0));
}
void test_1() {
const Matrix2x2 a(1,2,3,4),b(5,6,7,8); CHECK(a+b==Matrix2x2(6,8,10,12)); CHECK(b-a==Matrix2x2(4,4,4,4));
}
void test_2() {
const Matrix2x2 a(1,2,3,4),b(5,6,7,8); CHECK(a*b==Matrix2x2(19,22,43,50)); CHECK(b*a==Matrix2x2(23,34,31,46)); CHECK(a==Matrix2x2(1,2,3,4));
}
void test_3() {
const Matrix2x2 a(1,-2,3,4),id(1,0,0,1); CHECK(a*id==a && id*a==a); CHECK(a*Matrix2x2()==Matrix2x2());
}
void test_4() {
Matrix2x2 m; const auto& c=m; expect_throw<std::out_of_range>([&]{(void)m(2,0);}); expect_throw<std::out_of_range>([&]{(void)c(0,2);}); CHECK(m!=Matrix2x2(1,0,0,0));
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
