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
CHECK(minimum_of_three(1,3,4)==1); CHECK(minimum_of_three(3,1,4)==1); CHECK(minimum_of_three(3,4,1)==1);
}
void test_1() {
CHECK(minimum_of_three(-3,-3,1)==-3); CHECK(minimum_of_three(4,4,4)==4); CHECK(minimum_of_three(2.5,1.5,9.0)==1.5);
}
void test_2() {
struct X{int n; bool operator<(const X& r)const{return n<r.n;}}; CHECK(minimum_of_three(X{2},X{1},X{3}).n==1);
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
