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
auto r=inspect_stream("12 3.5 wrong"); CHECK(r.first==12 && r.second==3.5 && r.failed && !r.ended);
}
void test_1() {
auto r=inspect_stream("12 3.5 8"); CHECK(r.first==12 && r.second==3.5 && !r.failed && r.ended);
}
void test_2() {
auto r=inspect_stream("12 3.5 8 "); CHECK(!r.failed && !r.ended);
}
void test_3() {
auto r=inspect_stream("12 3.5"); CHECK(r.failed && r.ended);
}
void test_4() {
auto r=inspect_stream(""); CHECK(r.failed && r.ended && r.first==0); expect_throw<std::invalid_argument>([]{inspect_stream(nullptr);});
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
