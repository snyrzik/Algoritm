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

static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const ClockTime&>()),std::ostream&>);
static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<ClockTime&>()),std::istream&>);

void test_0() {
std::ostringstream out; const ClockTime a(7,5),b(23,59); CHECK(&(out<<a)==&out); out<<" | "<<b; CHECK(out.str()=="07:05 | 23:59");
}
void test_1() {
for(const auto& input:{std::pair<int,int>{0,0},{0,9},{9,0},{12,0}}){std::ostringstream out; out<<ClockTime(input.first,input.second); const std::string s=out.str(); CHECK(s.size()==5 && s[2]==':');} std::ostringstream out; out<<ClockTime(0,0); CHECK(out.str()=="00:00");
}
void test_2() {
for(const auto& p:{std::pair<int,int>{24,0},{-1,0},{12,60},{12,-1}}){bool caught=false; try{ClockTime value(p.first,p.second);(void)value;}catch(const std::invalid_argument&){caught=true;}catch(const std::out_of_range&){caught=true;}CHECK(caught);}
}
void test_3() {
std::istringstream in("07:05"); ClockTime value(1,2); CHECK(&(in>>value)==&in && !in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="07:05");
}
void test_4() {
std::istringstream in(" 07:05 23:59"); ClockTime a(1,1),b(2,2); in>>a>>b; CHECK(!in.fail()); std::ostringstream out; out<<a<<" | "<<b; CHECK(out.str()=="07:05 | 23:59");
}
void test_5() {
for(const char* input:{"24:00","12:60"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}
}
void test_6() {
for(const char* input:{"12;30","12:","12","",":30","xx:10"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}
}
void test_7() {
for(const char* input:{"7:05","07:5","-1:30","12:-1"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}
}
void test_8() {
ClockTime value(9,45); std::istringstream in("17:wrong"); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");
}
void test_9() {
std::ostringstream out; out.fill('*'); out.precision(3); const auto flags=out.flags(); out<<ClockTime(7,5); CHECK(out.str()=="07:05" && out.fill()=='*' && out.precision()==3 && out.flags()==flags); out<<" "<<std::setw(3)<<2; CHECK(out.str()=="07:05 **2");
}
void test_10() {
ClockTime a(1,2),b(3,4); std::istringstream in("08:09 24:00"); in>>a>>b; CHECK(in.fail()); std::ostringstream out; out<<a<<" | "<<b; CHECK(out.str()=="08:09 | 03:04");
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
        default:return 2;
        }
        CHECK(mastery_memory::live==before);
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"unexpected exception";return 1;}
}
