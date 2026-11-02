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
CHECK(maximum(2,9)==9 && maximum(-3,-7)==-3); CHECK(maximum(2.5,2.75)==2.75); CHECK(maximum(char(97),char(122))==char(122));
}
void test_1() {
CHECK(maximum(7,7)==7); CHECK(maximum<double>(2.5,3)==3.0); CHECK(maximum(2.5,static_cast<double>(2))==2.5);
}
void test_2() {
struct Item{int v; bool operator<(const Item& r)const{return v<r.v;}}; CHECK(maximum(Item{2},Item{8}).v==8);
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
