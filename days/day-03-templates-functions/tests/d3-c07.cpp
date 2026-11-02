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
void test_3() {
char storage[][8]={"z","aa","ba"}; const char* a=storage[0]; const char* b=storage[1]; CHECK(maximum(a,b)==a); CHECK(maximum(b,a)==a);
}
void test_4() {
const char a[]="same",b[]="same"; CHECK(maximum(static_cast<const char*>(a),static_cast<const char*>(b))==a); CHECK(std::strcmp(maximum("","x"),"x")==0);
}
void test_5() {
expect_throw<std::invalid_argument>([]{maximum(static_cast<const char*>(nullptr),"x");}); expect_throw<std::invalid_argument>([]{maximum("x",static_cast<const char*>(nullptr));});
}
void test_6() {
const char a[]="z",b[]="aa"; CHECK(maximum<const char*>(a,b)==a); expect_throw<std::invalid_argument>([]{maximum<const char*>(nullptr,"");});
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
case 5: test_5(); break;
case 6: test_6(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
