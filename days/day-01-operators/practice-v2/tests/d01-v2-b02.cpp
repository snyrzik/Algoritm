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
using F=AudioBlock(*)(const AudioBlock&,const ChannelMix&);using Chain=AudioBlock(*)(const AudioBlock&,const ChannelMix&,const ChannelMix&);using Same=bool(*)(const AudioBlock&,const AudioBlock&,double);
static_assert(std::is_same_v<decltype(static_cast<F>(&apply_filter)),F> && std::is_same_v<decltype(static_cast<Chain>(&apply_chain)),Chain> && std::is_same_v<decltype(static_cast<Same>(&approximately_same)),Same>);
void test_0(){
AudioBlock b;b.append(StereoSample(1,2));auto out=apply_filter(b,ChannelMix(2,0,0,3));CHECK(out[0]==StereoSample(2,6) && b[0]==StereoSample(1,2));
}
void test_1(){
AudioBlock b;b.append(StereoSample(1,2));b.append(StereoSample(-3,4));const ChannelMix a(2,0,0,3),s(0,1,1,0);auto out=apply_chain(b,a,s);CHECK(out[0]==StereoSample(6,2));CHECK(approximately_same(out,apply_filter(b,s*a),1e-9));CHECK(!approximately_same(out,apply_filter(b,a*s),1e-9));
}
void test_2(){
const AudioBlock b;auto out=apply_chain(b,ChannelMix(),ChannelMix(2,3,4,5));CHECK(out.empty() && approximately_same(b,out,0));
}
void test_3(){
AudioBlock b;for(int i=0;i<4;++i)b.append(StereoSample(i+1,-i));auto out=apply_chain(b,ChannelMix(),ChannelMix(0,1,1,0));CHECK(out.size()==4 && out[3]==StereoSample(-3,4));CHECK(b[3]==StereoSample(4,-3));
}
void test_4(){
AudioBlock a,b;a.append(StereoSample(1,2));CHECK(!approximately_same(a,b,1e-9));b.append(StereoSample(1,2));CHECK(approximately_same(a,b,0));b[0][0]+=0.5e-9;CHECK(!approximately_same(a,b,0) && approximately_same(a,b,1e-9));
}
void test_5(){
AudioBlock a,b;a.append(StereoSample(1,2));a.append(StereoSample(3,4));b=a;b[1][1]+=0.1;CHECK(!approximately_same(a,b,1e-9));
}
void test_6(){
const AudioBlock a;expect_throw<std::invalid_argument>([&]{approximately_same(a,a,-1);});
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
