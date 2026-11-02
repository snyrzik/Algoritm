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
const Polynomial2 p(2,3,4); CHECK(p[0]==4 && p[1]==3 && p[2]==2);
}
void test_9() {
const Polynomial2 p(2,3,4); CHECK(p(0)==4 && p(2)==18 && p(-1)==3);
}
void test_10() {
const Polynomial2 p(2,3,4),q(1,2,3); CHECK((p+q)==Polynomial2(3,5,7)); CHECK((p-q)==Polynomial2(1,1,1)); CHECK(-p==Polynomial2(-2,-3,-4)); CHECK(+p==p);
}
void test_11() {
const Polynomial2 p(2,3,4); CHECK(2.0*p==Polynomial2(4,6,8)); CHECK(p*0==Polynomial2());
}
void test_12() {
Polynomial2 p; p[2]=3; p[1]=2; p[0]=1; const auto& c=p; CHECK(c(2)==17); expect_throw<std::out_of_range>([&]{(void)c[3];}); expect_throw<std::out_of_range>([&]{(void)p[3];});
}
void test_13() {
std::ostringstream o; const Polynomial2 p(2,3,4); CHECK(&(o<<p)==&o); CHECK(o.str()=="[2,3,4]"); CHECK(p!=Polynomial2());
}
void test_14() {
Matrix2x2 m(1,2,3,4); m(1,0)=7; const auto& c=m; CHECK(c(0,1)==2 && c(1,0)==7); CHECK(Matrix2x2()==Matrix2x2(0,0,0,0));
}
void test_15() {
const Matrix2x2 a(1,2,3,4),b(5,6,7,8); CHECK(a+b==Matrix2x2(6,8,10,12)); CHECK(b-a==Matrix2x2(4,4,4,4));
}
void test_16() {
const Matrix2x2 a(1,2,3,4),b(5,6,7,8); CHECK(a*b==Matrix2x2(19,22,43,50)); CHECK(b*a==Matrix2x2(23,34,31,46)); CHECK(a==Matrix2x2(1,2,3,4));
}
void test_17() {
const Matrix2x2 a(1,-2,3,4),id(1,0,0,1); CHECK(a*id==a && id*a==a); CHECK(a*Matrix2x2()==Matrix2x2());
}
void test_18() {
Matrix2x2 m; const auto& c=m; expect_throw<std::out_of_range>([&]{(void)m(2,0);}); expect_throw<std::out_of_range>([&]{(void)c(0,2);}); CHECK(m!=Matrix2x2(1,0,0,0));
}
void test_19() {
const Vector3 v(1,2,3); const Matrix2x2 m(1,2,3,4); const Polynomial2 p(1,0,1); CHECK(transform(v,m,p)==Vector3(26,122,10)); CHECK(v==Vector3(1,2,3));
}
void test_20() {
CHECK(transform(Vector3(-1,2,0),Matrix2x2(1,0,0,1),Polynomial2(0,1,0))==Vector3(-1,2,0)); CHECK(transform(Vector3(1,2,3),Matrix2x2(),Polynomial2(0,1,0))==Vector3(0,0,3));
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
case 9: test_9(); break;
case 10: test_10(); break;
case 11: test_11(); break;
case 12: test_12(); break;
case 13: test_13(); break;
case 14: test_14(); break;
case 15: test_15(); break;
case 16: test_16(); break;
case 17: test_17(); break;
case 18: test_18(); break;
case 19: test_19(); break;
case 20: test_20(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
