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
const Vector3 z; CHECK(z[0]==0 && z[1]==0 && z[2]==0); const Vector3 v(1,2,3); CHECK(v[0]==1 && v[2]==3);
}
void test_1() {
const Vector3 a(1,2,3),b(4,5,6); const auto c=a+b; CHECK(c==Vector3(5,7,9)); CHECK(a==Vector3(1,2,3) && b==Vector3(4,5,6));
}
void test_2() {
const Vector3 a(1,-2,3); CHECK(-a==Vector3(-1,2,-3)); CHECK(+a==a); CHECK(a-a==Vector3());
}
void test_3() {
const Vector3 v(2,-4,6); CHECK(v*0.5==Vector3(1,-2,3)); CHECK(-2.0*v==Vector3(-4,8,-12)); CHECK(0.0*v==Vector3());
}
void test_4() {
Vector3 v; v[1]=9; const Vector3& c=v; CHECK(c[1]==9); CHECK(&v[1]==&c[1]);
}
void test_5() {
Vector3 v; const Vector3& c=v; expect_throw<std::out_of_range>([&]{(void)v[3];}); expect_throw<std::out_of_range>([&]{(void)c[std::numeric_limits<std::size_t>::max()];});
}
void test_6() {
CHECK(Vector3(1,2,3)!=Vector3(1,2,4)); CHECK(!(Vector3(1,2,3)!=Vector3(1,2,3)));
}
void test_7() {
std::ostringstream out; const Vector3 a(1,2,3),b(-1,0,4); CHECK(&(out<<a)==&out); out<<" | "<<b; CHECK(out.str()=="(1,2,3) | (-1,0,4)");
}
void test_8() {
const Vector3 a(1.25,2,3); std::ostringstream o; o.setf(std::ios::fixed); o.precision(2); o<<a; CHECK(o.str()=="(1.25,2.00,3.00)"); std::cout<<a;
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
case 7: test_7(); break;
case 8: test_8(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
