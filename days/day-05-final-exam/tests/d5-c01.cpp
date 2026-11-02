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
static_assert(std::is_same_v<decltype(std::declval<TSequence<int>&>()[0]),int&>); static_assert(std::is_same_v<decltype(std::declval<const TSequence<int>&>()[0]),const int&>);
void test_0() {
const TSequence<int> s; CHECK(s.size()==0 && s.empty()); std::ostringstream o; o<<s; CHECK(o.str()=="[]");
}
void test_1() {
const TSequence<int> s(3); CHECK(s.size()==3 && s[0]==0 && s[2]==0); const TSequence<double> d(2); CHECK(d[1]==0.0);
}
void test_2() {
TSequence<int> s; for(int i=0;i<100;++i)s.push_back(i*2); CHECK(s.size()==100); for(int i=0;i<100;++i)CHECK(s[static_cast<std::size_t>(i)]==i*2);
}
void test_3() {
TSequence<int> s; s.push_back(2); s.push_back(4); s.insert(0,1); s.insert(2,3); s.insert(s.size(),5); CHECK(s.size()==5); for(std::size_t i=0;i<5;++i)CHECK(s[i]==static_cast<int>(i)+1);
}
void test_4() {
TSequence<int> s; for(int i=1;i<=4;++i)s.push_back(i); s.erase(0); s.erase(s.size()-1); CHECK(s.size()==2 && s[0]==2 && s[1]==3); s.erase(1); s.erase(0); CHECK(s.empty());
}
void test_5() {
TSequence<int> a; a.push_back(1); a.push_back(2); TSequence<int> b(a); b[0]=9; CHECK(a[0]==1 && b[0]==9);
}
void test_6() {
TSequence<int> a,b,c; c.push_back(7); CHECK(&(a=b=c)==&a); b[0]=3; CHECK(a[0]==7 && c[0]==7); a=mastery_alias(a); CHECK(a.size()==1 && a[0]==7);
}
void test_7() {
TSequence<int> a; TSequence<int> b(a); b.push_back(8); CHECK(a.empty() && b.size()==1); TSequence<int> c(4); c=a; CHECK(c.empty());
}
void test_8() {
TSequence<int> s; expect_throw<std::out_of_range>([&]{(void)s[0];}); expect_throw<std::out_of_range>([&]{s.erase(0);}); expect_throw<std::out_of_range>([&]{s.insert(1,3);}); s.push_back(7); const auto& c=s; expect_throw<std::out_of_range>([&]{(void)c[1];}); expect_throw<std::out_of_range>([&]{s.erase(1);}); CHECK(s.size()==1 && s[0]==7);
}
void test_9() {
TSequence<std::string> s; s.push_back("first"); for(int i=0;i<32;++i)s.push_back(s[0]); CHECK(s.size()==33); for(std::size_t i=0;i<s.size();++i)CHECK(s[i]=="first");
}
void test_10() {
TSequence<std::string> s; s.push_back("a"); s.push_back("b"); s.insert(0,s[1]); CHECK(s.size()==3 && s[0]=="b" && s[1]=="a" && s[2]=="b");
}
void test_11() {
TSequence<double> s; s.push_back(2.5); s.push_back(-1.25); const auto& c=s; CHECK(c[0]+c[1]==1.25);
}
void test_12() {
const int before=Tracked::alive; {TSequence<Tracked> s; Tracked t(4); s.push_back(t); s.push_back(t); TSequence<Tracked> b(s); b.erase(0); CHECK(b[0].value==4 && s.size()==2);} CHECK(Tracked::alive==before);
}
void test_13() {
TSequence<int> a; a.push_back(1); a.push_back(2); auto b=a; CHECK(a==b && !(a!=b)); b[1]=3; CHECK(a!=b); std::ostringstream o; CHECK(&(o<<a)==&o); CHECK(o.str()=="[1,2]");
}
void test_14() {
TSequence<Tracked> s; Tracked a(1),b(2); s.push_back(a); const int alive=Tracked::alive; Tracked::copies_before_throw=0; bool caught=false; try{s.push_back(b);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && s.size()==1 && s[0].value==1 && Tracked::alive==alive);
}
void test_15() {
TSequence<Tracked> s; Tracked t(4); s.push_back(t); s.push_back(t); const int alive=Tracked::alive; Tracked::copies_before_throw=1; bool caught=false; try{TSequence<Tracked> copy(s);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && Tracked::alive==alive && s.size()==2);
}
void test_16() {
TSequence<Tracked> a,b; a.push_back(Tracked(1)); b.push_back(Tracked(9)); b.push_back(Tracked(8)); const int alive=Tracked::alive; Tracked::copies_before_throw=1; bool caught=false; try{a=b;}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && a.size()==1 && a[0].value==1 && Tracked::alive==alive);
}
void test_17() {
TSequence<Tracked> s; s.push_back(Tracked(1)); s.push_back(Tracked(2)); Tracked v(3); const int alive=Tracked::alive; Tracked::copies_before_throw=1; bool caught=false; try{s.insert(0,v);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; CHECK(caught && s.size()==2 && s[0].value==1 && s[1].value==2 && Tracked::alive==alive);
}
void test_18() {
TSequence<Tracked> s; s.push_back(Tracked(1)); s.push_back(Tracked(2)); s.push_back(Tracked(3)); const int alive=Tracked::alive; Tracked::copies_before_throw=0; bool caught=false; try{s.erase(0);}catch(const std::runtime_error&){caught=true;} Tracked::copies_before_throw=-1; if(caught){CHECK(s.size()==3 && s[0].value==1 && s[2].value==3 && Tracked::alive==alive);}else{CHECK(s.size()==2 && s[0].value==2 && s[1].value==3);}
}
void test_19() {
expect_throw<std::length_error>([]{TSequence<double> s(std::numeric_limits<std::size_t>::max());});
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
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
