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
