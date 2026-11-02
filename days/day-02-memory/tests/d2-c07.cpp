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
const CMyString s; CHECK(s.size()==0 && s.c_str()!=nullptr && s.c_str()[0]==0);
}
void test_1() {
char raw[]="hello"; const CMyString s(raw); raw[0]=char(88); CHECK(s.size()==5 && std::strcmp(s.c_str(),"hello")==0 && s.c_str()[s.size()]==0);
}
void test_2() {
CMyString a("cat"); CMyString b(a); b[0]=char(98); CHECK(std::strcmp(a.c_str(),"cat")==0 && std::strcmp(b.c_str(),"bat")==0);
}
void test_3() {
CMyString a("a"),b("bb"),c("ccc"); CHECK(&(a=b=c)==&a); b[0]=char(88); CHECK(std::strcmp(a.c_str(),"ccc")==0); a=mastery_alias(a); CHECK(std::strcmp(a.c_str(),"ccc")==0);
}
void test_4() {
CMyString outside; {CMyString inside("alive"); outside=inside;} CHECK(std::strcmp(outside.c_str(),"alive")==0);
}
void test_5() {
expect_throw<std::invalid_argument>([]{CMyString s(nullptr);}); CMyString a("a"); const auto& b=a; expect_throw<std::out_of_range>([&]{(void)a[1];}); expect_throw<std::out_of_range>([&]{(void)b[9];});
}
void test_6() {
CHECK(CMyString("same")==CMyString("same")); CHECK(CMyString("a")!=CMyString("aa")); CHECK(CMyString()==CMyString(""));
}
void test_7() {
for(int i=0;i<100;++i){CMyString a("resource"); CMyString b(a); CMyString c; c=b; CHECK(c==a);}
}
void test_8() {
CMyString a("old"),b("replacement"); mastery_memory::fail_after=0; bool caught=false; try{a=b;}catch(const std::bad_alloc&){caught=true;} mastery_memory::fail_after=-1; if(caught){CHECK(std::strcmp(a.c_str(),"old")==0);}else{CHECK(std::strcmp(a.c_str(),"replacement")==0);}
}
void test_9() {
CMyString s("ABCDE"); s.replace_range(1,2,s.c_str()+3); CHECK(s==CMyString("ADEDE"));
}
void test_10() {
CMyString s("abcde"); s.replace_range(1,3,"X"); CHECK(s==CMyString("aXe")); s.replace_range(1,1,"12345"); CHECK(s==CMyString("a12345e"));
}
void test_11() {
CMyString s("abc"); s.replace_range(0,3,""); CHECK(s==CMyString()); s.replace_range(0,0,"xy"); s.replace_range(2,0,"z"); CHECK(s==CMyString("xyz"));
}
void test_12() {
CMyString s("abc"); expect_throw<std::invalid_argument>([&]{s.replace_range(0,1,nullptr);}); expect_throw<std::out_of_range>([&]{s.replace_range(2,2,"x");}); CHECK(s==CMyString("abc"));
}
void test_13() {
CMyString s("old"); mastery_memory::fail_after=0; bool caught=false; try{s.replace_range(0,1,"a much longer replacement");}catch(const std::bad_alloc&){caught=true;} mastery_memory::fail_after=-1; if(caught){CHECK(std::strcmp(s.c_str(),"old")==0);}else{CHECK(std::strcmp(s.c_str(),"a much longer replacementld")==0);}
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
