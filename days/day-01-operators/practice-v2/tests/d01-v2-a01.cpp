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
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>().left()),double> && std::is_same_v<decltype(std::declval<const StereoSample&>().right()),double>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()[0]),double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()[0]),const double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()+std::declval<const StereoSample&>()),StereoSample>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()+=std::declval<const StereoSample&>()),StereoSample&> && std::is_same_v<decltype(std::declval<StereoSample&>()-=std::declval<const StereoSample&>()),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const StereoSample&>()),std::ostream&>);
void test_0(){
const StereoSample a;const StereoSample b(2,-1);CHECK(a.left()==0 && a.right()==0);CHECK(b.left()==2 && b.right()==-1);
}
void test_1(){
const StereoSample a(2,-1),b(3,4);CHECK(a+b==StereoSample(5,3));CHECK(a-b==StereoSample(-1,-5));CHECK(a==StereoSample(2,-1) && b==StereoSample(3,4));
}
void test_2(){
const StereoSample a(2,-1);CHECK(-a==StereoSample(-2,1));CHECK(a==StereoSample(2,-1));
}
void test_3(){
const StereoSample a(1,-2);CHECK(a*0.5==StereoSample(0.5,-1));CHECK(0.5*a==StereoSample(0.5,-1));CHECK(-2.0*a==StereoSample(-2,4));CHECK(0.0*a==StereoSample());
}
void test_4(){
StereoSample a(1,2);const StereoSample b(2,3),c(4,5);CHECK(&((a+=b)+=c)==&a && a==StereoSample(7,10));CHECK(&((a-=b)-=c)==&a && a==StereoSample(1,2));
}
void test_5(){
StereoSample a(2,-3);a+=a;CHECK(a==StereoSample(4,-6));a-=a;CHECK(a==StereoSample());
}
void test_6(){
StereoSample a(1,2);a[1]=7.5;const StereoSample& c=a;CHECK(c[0]==1 && c[1]==7.5);CHECK(&a[0]==&c[0]);
}
void test_7(){
StereoSample a(1,2);const auto& c=a;expect_throw<std::out_of_range>([&]{a[2]=3;});expect_throw<std::out_of_range>([&]{(void)c[2];});CHECK(a==StereoSample(1,2));
}
void test_8(){
const StereoSample a(1,2);expect_throw<std::out_of_range>([&]{(void)a[std::numeric_limits<std::size_t>::max()];});
}
void test_9(){
CHECK(StereoSample(0,0)==StereoSample(1e-9,-1e-9));CHECK(StereoSample(0,0)!=StereoSample(1.01e-9,0));CHECK(StereoSample(1.1,0)!=StereoSample(1.9,0));CHECK(!(StereoSample(2,3)!=StereoSample(2,3)));
}
void test_10(){
const StereoSample a(1.25,-2.5),b(3,4);std::ostringstream out;CHECK(&(out<<a)==&out);out<<" | "<<b;std::istringstream in(out.str());char p=0,comma=0,q=0,bar=0;double l=0,r=0;in>>p>>l>>comma>>r>>q>>bar;CHECK(p==char(40) && comma==char(44) && q==char(41) && bar==char(124) && close_value(l,1.25) && close_value(r,-2.5));
}
void test_11(){
std::ostringstream out;out<<std::fixed<<std::setprecision(2)<<StereoSample(1.25,-2);CHECK(out.str()=="(1.25,-2.00)");
}
void test_12(){
StereoSample a(2,3);auto b=a;b[0]=9;CHECK(a.left()==2 && b.left()==9);StereoSample c;c=a;c[1]=7;CHECK(a.right()==3);
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
case 10:test_10();break;
case 11:test_11();break;
case 12:test_12();break;
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
