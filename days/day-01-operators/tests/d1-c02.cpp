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
const Polynomial2 p(2,3,4); CHECK(p[0]==4 && p[1]==3 && p[2]==2);
}
void test_1() {
const Polynomial2 p(2,3,4); CHECK(p(0)==4 && p(2)==18 && p(-1)==3);
}
void test_2() {
const Polynomial2 p(2,3,4),q(1,2,3); CHECK((p+q)==Polynomial2(3,5,7)); CHECK((p-q)==Polynomial2(1,1,1)); CHECK(-p==Polynomial2(-2,-3,-4)); CHECK(+p==p);
}
void test_3() {
const Polynomial2 p(2,3,4); CHECK(2.0*p==Polynomial2(4,6,8)); CHECK(p*0==Polynomial2());
}
void test_4() {
Polynomial2 p; p[2]=3; p[1]=2; p[0]=1; const auto& c=p; CHECK(c(2)==17); expect_throw<std::out_of_range>([&]{(void)c[3];}); expect_throw<std::out_of_range>([&]{(void)p[3];});
}
void test_5() {
std::ostringstream o; const Polynomial2 p(2,3,4); CHECK(&(o<<p)==&o); CHECK(o.str()=="[2,3,4]"); CHECK(p!=Polynomial2());
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
