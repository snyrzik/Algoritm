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
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>().size()),std::size_t>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>()[0]),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()[0]),const StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>().append(std::declval<const StereoSample&>())),bool>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()(std::declval<const ChannelMix&>())),AudioBlock>);
void test_0(){
const AudioBlock b;CHECK(b.size()==0 && b.empty() && !b.full() && b.average_power()==0);
}
void test_1(){
AudioBlock b;CHECK(b.append(StereoSample(1,1)) && b.append(StereoSample(3,1)));CHECK(b.size()==2 && !b.empty() && !b.full() && close_value(b.average_power(),3));
}
void test_2(){
AudioBlock b;for(int i=0;i<4;++i)CHECK(b.append(StereoSample(i,-i)));CHECK(b.full() && b.size()==4);CHECK(!b.append(StereoSample(99,99)));for(std::size_t i=0;i<4;++i)CHECK(b[i].left()==static_cast<double>(i));
}
void test_3(){
AudioBlock b;expect_throw<std::out_of_range>([&]{(void)b[0];});b.append(StereoSample(1,2));const AudioBlock& c=b;expect_throw<std::out_of_range>([&]{(void)b[1];});expect_throw<std::out_of_range>([&]{(void)c[3];});
}
void test_4(){
AudioBlock b;b.append(StereoSample(1,2));b[0][1]=7;const auto& c=b;CHECK(c[0].left()==1 && c[0].right()==7);
}
void test_5(){
AudioBlock b;b.append(StereoSample(1,2));b.append(StereoSample(-3,4));const auto& c=b;const ChannelMix gain(2,0,0,3);auto out=c(gain);CHECK(out.size()==2 && out[0].left()==2 && out[0].right()==6 && out[1].left()==-6 && out[1].right()==12);CHECK(c[0].left()==1 && c[0].right()==2);
}
void test_6(){
AudioBlock a;a.append(StereoSample(1,2));auto b=a;b[0][0]=9;CHECK(a[0].left()==1);AudioBlock c;c=a;c[0][1]=8;CHECK(a[0].right()==2);
}
void test_7(){
AudioBlock b;b.append(StereoSample(-2,4));CHECK(close_value(b.average_power(),10));b.append(StereoSample(0,0));CHECK(close_value(b.average_power(),5));
}
void test_8(){
const AudioBlock empty;const auto out=empty(ChannelMix(2,3,4,5));CHECK(out.empty() && out.size()==0 && out.average_power()==0);
}
void test_9(){
const long before=mastery_memory::live;{AudioBlock b;CHECK(b.append(StereoSample(1,2)));CHECK(mastery_memory::live==before);}CHECK(mastery_memory::live==before);
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
case 7:test_7();break;
case 8:test_8();break;
case 9:test_9();break;
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
