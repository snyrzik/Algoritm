#include "candidate.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <type_traits>
#include <limits>
#include <utility>
#include <string>
#include "support.hpp"
inline void require_contract(bool ok,const char* contract){if(!ok)throw std::runtime_error(contract);}
inline bool close_value(double a,double b,double eps=1e-9){return std::abs(a-b)<=eps;}

#undef CHECK
#define CHECK(...) do {if(!(__VA_ARGS__))throw std::runtime_error("Contract not satisfied; see the named check");}while(false)
static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<StereoSample&>()),std::istream&>);
static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<ChannelMix&>()),std::istream&>);
void test_0(){
for(const char* s:{"(1.5,-2)","( 1.5 , -2 )"}){StereoSample a(7,8);std::istringstream in(s);CHECK(&(in>>a)==&in && !in.fail() && a==StereoSample(1.5,-2));}
}
void test_1(){
for(const char* s:{"(1;2)","(1,)","(bad,2)","(1,2","bad",""}){StereoSample a(7,8);std::istringstream in(s);in>>a;CHECK(in.fail() && a==StereoSample(7,8));}
}
void test_2(){
StereoSample a,b;std::istringstream in("(1,2) (3,4)");in>>a>>b;CHECK(!in.fail() && a==StereoSample(1,2) && b==StereoSample(3,4));
}
void test_3(){
for(const char* s:{"[[1,2],[3,4]]","[[ 1 , 2 ], [ 3 , 4 ]]"}){ChannelMix a;std::istringstream in(s);CHECK(&(in>>a)==&in && !in.fail() && a==ChannelMix(1,2,3,4));}
}
void test_4(){
for(const char* s:{"[[1,2],(3,4)]","[[1,2],[3]]","[[1;2],[3,4]]","[[1,2],[3,4]","[[1,2],[bad,4]]",""}){ChannelMix a(7,8,9,10);std::istringstream in(s);in>>a;CHECK(in.fail() && a==ChannelMix(7,8,9,10));}
}
void test_5(){
ChannelMix a,b;std::istringstream in("[[1,0],[0,1]] [[2,0],[0,3]]");in>>a>>b;CHECK(!in.fail() && a==ChannelMix() && b==ChannelMix(2,0,0,3));
}
void test_6(){
StereoSample a(7,8),b(9,10);std::istringstream in("(1,2) (3;4)");in>>a>>b;CHECK(in.fail() && a==StereoSample(1,2) && b==StereoSample(9,10));
}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    try{
        {std::ostringstream warm;warm<<std::setprecision(3)<<1.25;
         std::istringstream input("1.25 2");double decimal=0;int integer=0;input>>decimal>>integer;}
        const auto before=mastery_memory::live;
        switch(std::stoi(argv[1])){
case 0:test_0();break;
case 1:test_1();break;
case 2:test_2();break;
case 3:test_3();break;
case 4:test_4();break;
case 5:test_5();break;
case 6:test_6();break;
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
