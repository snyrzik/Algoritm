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
#include <functional>
#include <iomanip>

static_assert(std::is_same_v<decltype(std::declval<FixedHistory&>()[0]),int&>);
static_assert(std::is_same_v<std::remove_cv_t<std::remove_reference_t<decltype(std::declval<const FixedHistory&>()[0])>>,int>);
static_assert(!std::is_assignable_v<decltype(std::declval<const FixedHistory&>()[0]),int>, "Const object must not expose writable elements");
static_assert(std::is_same_v<decltype(std::declval<const FixedHistory&>()(0,1)),int>);

void test_0() {
const FixedHistory h(10,-20,30,0); CHECK(h[0]==10 && h[1]==-20 && h[2]==30 && h[3]==0);
}
void test_1() {
FixedHistory h(1,2,3,4); int& element=h[2]; element=100; CHECK(h[2]==100); h[2]=77; CHECK(element==77);
}
void test_2() {
FixedHistory h(1,2,3,4); const FixedHistory& read=h; h[1]=55; CHECK(read[1]==55 && read[0]==1);
}
void test_3() {
const FixedHistory h(2,5,-7,11); CHECK(h(0,3)==13 && h(1,2)==-2 && h(3,3)==22); CHECK(h[0]==2 && h[3]==11);
}
void test_4() {
FixedHistory h(1,2,3,4); h.swap_indices(0,3); CHECK(h[0]==4 && h[3]==1); h.swap_indices(1,2); CHECK(h[1]==3 && h[2]==2);
}
void test_5() {
FixedHistory h(1,2,3,4); h.swap_indices(2,2); CHECK(h[0]==1 && h[1]==2 && h[2]==3 && h[3]==4);
}
void test_6() {
FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{h[4]=99;}); expect_throw<std::out_of_range>([&]{(void)h[9];}); CHECK(h[0]==1 && h[3]==4);
}
void test_7() {
const FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{(void)h[4];});
}
void test_8() {
const FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{(void)h(4,0);}); expect_throw<std::out_of_range>([&]{(void)h(0,4);});
}
void test_9() {
FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{h.swap_indices(1,4);}); CHECK(h[0]==1 && h[1]==2 && h[2]==3 && h[3]==4); expect_throw<std::out_of_range>([&]{h.swap_indices(4,1);}); CHECK(h[1]==2);
}
void test_10() {
FixedHistory h(1,2,3,4); auto copy=h; copy[0]=99; CHECK(h[0]==1 && copy[0]==99);
}
void test_11() {
const long before=mastery_memory::live; {FixedHistory h(1,2,3,4); CHECK(mastery_memory::live==before); h.swap_indices(0,3); CHECK(mastery_memory::live==before);} CHECK(mastery_memory::live==before);
}
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    try {
        // Some standard-library implementations cache numeric locale facets.
        // Initialize those before counting allocations owned by the exercise.
        { std::ostringstream warm; warm.fill('*'); warm<<std::setw(3)<<2; }
        const long before=mastery_memory::live;
        switch(std::stoi(argv[1])) {
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
        default:return 2;
        }
        CHECK(mastery_memory::live==before);
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"unexpected exception";return 1;}
}
