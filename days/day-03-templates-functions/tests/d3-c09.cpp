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
int a[]={-1,2,3,4}; auto even=[](int x){return x%2==0;}; CHECK(find_first(a,4,even)==1 && count_if(a,4,even)==2); CHECK(find_first(a,4,[](int x){return x>9;})==4);
}
void test_1() {
CHECK(find_first<int>(nullptr,0,[](int){return true;})==0); CHECK(count_if<int>(nullptr,0,[](int){return true;})==0);
}
void test_2() {
int a[]={1,2,3}; swap_at(a,3,0,2); CHECK(a[0]==3 && a[2]==1); swap_at(a,3,1,1); CHECK(a[1]==2);
}
void test_3() {
int a[]={1,2}; expect_throw<std::out_of_range>([&]{swap_at(a,2,0,2);}); CHECK(a[0]==1 && a[1]==2); expect_throw<std::invalid_argument>([]{swap_at<int>(nullptr,1,0,0);}); expect_throw<std::invalid_argument>([]{count_if<int>(nullptr,1,[](int){return true;});});
}
void test_4() {
std::string a[]={"x","long","hi"}; CHECK(find_first(a,3,[](const std::string& s){return s.size()>2;})==1);
}
void test_5() {
CHECK(maximum(2,9)==9 && maximum(-3,-7)==-3); CHECK(maximum(2.5,2.75)==2.75); CHECK(maximum(char(97),char(122))==char(122));
}
void test_6() {
CHECK(maximum(7,7)==7); CHECK(maximum<double>(2.5,3)==3.0); CHECK(maximum(2.5,static_cast<double>(2))==2.5);
}
void test_7() {
struct Item{int v; bool operator<(const Item& r)const{return v<r.v;}}; CHECK(maximum(Item{2},Item{8}).v==8);
}
void test_8() {
CHECK(minimum_of_three(1,3,4)==1); CHECK(minimum_of_three(3,1,4)==1); CHECK(minimum_of_three(3,4,1)==1);
}
void test_9() {
CHECK(minimum_of_three(-3,-3,1)==-3); CHECK(minimum_of_three(4,4,4)==4); CHECK(minimum_of_three(2.5,1.5,9.0)==1.5);
}
void test_10() {
struct X{int n; bool operator<(const X& r)const{return n<r.n;}}; CHECK(minimum_of_three(X{2},X{1},X{3}).n==1);
}
void test_11() {
int a[]={1,3,4},b[]={4,3,1}; CHECK(index_of_min(a,3)==0 && index_of_min(b,3)==2);
}
void test_12() {
int a[]={3,1,1,2}; CHECK(index_of_min(a,4)==1); double b[]={2.5}; CHECK(index_of_min(b,1)==0);
}
void test_13() {
int a[]={1}; expect_throw<std::invalid_argument>([&]{index_of_min(a,0);}); expect_throw<std::invalid_argument>([]{index_of_min<int>(nullptr,1);});
}
void test_14() {
std::string a[]={"z","az","ba"}; CHECK(index_of_min(a,3)==1);
}
void test_15() {
const Polynomial2 p(2,3,4); CHECK(p[0]==4 && p[1]==3 && p[2]==2);
}
void test_16() {
const Polynomial2 p(2,3,4); CHECK(p(0)==4 && p(2)==18 && p(-1)==3);
}
void test_17() {
const Polynomial2 p(2,3,4),q(1,2,3); CHECK((p+q)==Polynomial2(3,5,7)); CHECK((p-q)==Polynomial2(1,1,1)); CHECK(-p==Polynomial2(-2,-3,-4)); CHECK(+p==p);
}
void test_18() {
const Polynomial2 p(2,3,4); CHECK(2.0*p==Polynomial2(4,6,8)); CHECK(p*0==Polynomial2());
}
void test_19() {
Polynomial2 p; p[2]=3; p[1]=2; p[0]=1; const auto& c=p; CHECK(c(2)==17); expect_throw<std::out_of_range>([&]{(void)c[3];}); expect_throw<std::out_of_range>([&]{(void)p[3];});
}
void test_20() {
std::ostringstream o; const Polynomial2 p(2,3,4); CHECK(&(o<<p)==&o); CHECK(o.str()=="[2,3,4]"); CHECK(p!=Polynomial2());
}
void test_21() {
Polynomial2 a[]={Polynomial2(1,0,0),Polynomial2(0,2,1)}; CHECK(find_first(a,2,[](const Polynomial2& p){return p[2]==0;})==1); swap_at(a,2,0,1); CHECK(a[0](2)==5);
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
case 21: test_21(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
