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
Rectangle r(3,4); Circle c(2); const Shape& a=r; const Shape& b=c; CHECK(a.area()==12); CHECK(std::abs(b.area()-12.566370614359172)<1e-10);
}
void test_1() {
Rectangle r(2,4); Shape* b=upcast(&r); CHECK(as_rectangle(b)==&r && &require_rectangle(*b)==&r);
}
void test_2() {
Circle c(1); CHECK(as_rectangle(&c)==nullptr && as_rectangle(nullptr)==nullptr); expect_throw<std::bad_cast>([&]{require_rectangle(c);});
}
void test_3() {
Circle c(2); Rectangle r(2,2); struct Sub:Circle{Sub():Circle(1){}}; Sub sub; CHECK(is_exact_circle(c) && !is_exact_circle(r) && !is_exact_circle(sub));
}
void test_4() {
CHECK(Circle(0).area()==0 && Rectangle(0,2).area()==0); expect_throw<std::invalid_argument>([]{Circle c(-1);}); expect_throw<std::invalid_argument>([]{Rectangle r(1,-2);});
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
