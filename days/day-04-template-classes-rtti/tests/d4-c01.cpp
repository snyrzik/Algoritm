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
static_assert(std::is_same_v<decltype(std::declval<const Box<int>&>().get()),const int&>);
void test_0() {
Box<int> a(3); a.set(7); CHECK(a.get()==7); const Box<double> b(2.5); CHECK(b.get()==2.5);
}
void test_1() {
Box<std::string> a("a"); auto b=a; b.set("b"); CHECK(a.get()=="a" && b.get()=="b");
}
void test_2() {
const Box<int> a(4); CHECK(&a.get()==&a.get());
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
