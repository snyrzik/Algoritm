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
static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()(std::declval<const StereoSample&>())),StereoSample>);
static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()*std::declval<const ChannelMix&>()),ChannelMix>);
static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()==std::declval<const ChannelMix&>()),bool>);
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const ChannelMix&>()),std::ostream&>);
void test_0(){
const ChannelMix id;const StereoSample s(3,-2);auto r=id(s);CHECK(close_value(r.left(),3) && close_value(r.right(),-2));
}
void test_1(){
const ChannelMix swap(0,1,1,0),gain(2,0,0,3);const auto a=swap(StereoSample(3,-2));const auto b=gain(StereoSample(1,2));CHECK(close_value(a.left(),-2) && close_value(a.right(),3));CHECK(close_value(b.left(),2) && close_value(b.right(),6));
}
void test_2(){
const ChannelMix swap(0,1,1,0),gain(2,0,0,3);const StereoSample s(1,2);auto a=(swap*gain)(s),b=(gain*swap)(s);CHECK(close_value(a.left(),6) && close_value(a.right(),2));CHECK(close_value(b.left(),4) && close_value(b.right(),3));
}
void test_3(){
const ChannelMix a(1,2,-3,4),b(2,-1,5,3);CHECK(a*b==ChannelMix(12,5,14,15));CHECK(b*a==ChannelMix(5,0,-4,22));
}
void test_4(){
const ChannelMix a(1.5,-2,0.25,3),b(-1,4,2,0.5);for(const auto& s:{StereoSample(1,2),StereoSample(-3,0.5),StereoSample(0,0)}){const auto x=(a*b)(s),y=a(b(s));CHECK(close_value(x.left(),y.left()) && close_value(x.right(),y.right()));}
}
void test_5(){
const ChannelMix a(1,2,3,4),b(5,6,7,8);const StereoSample s(2,-1);(void)(a*b);(void)a(s);CHECK(a==ChannelMix(1,2,3,4) && b==ChannelMix(5,6,7,8));CHECK(s.left()==2 && s.right()==-1);
}
void test_6(){
CHECK(ChannelMix(0,0,0,0)==ChannelMix(1e-9,0,0,-1e-9));CHECK(ChannelMix(0,0,0,0)!=ChannelMix(0,0,1.1e-9,0));CHECK(!(ChannelMix()!=ChannelMix()));
}
void test_7(){
std::ostringstream out;const ChannelMix a(1.25,-2,3,4);CHECK(&(out<<a)==&out);std::istringstream in(out.str());char x[8]{};double a0=0,b0=0,c0=0,d0=0;in>>x[0]>>x[1]>>a0>>x[2]>>b0>>x[3]>>x[4]>>x[5]>>c0>>x[6]>>d0>>x[7];char last=0;in>>last;CHECK(!in.fail() && close_value(a0,1.25) && b0==-2 && c0==3 && d0==4);CHECK(std::string(x,8)=="[[,],[,]" && last==char(93));
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
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
