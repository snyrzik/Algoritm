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
static_assert(std::is_same_v<decltype(std::declval<Meter&>()+=std::declval<const Meter&>()),Meter&>);
void test_0(){
Meter a(1);const Meter b(2),c(4);CHECK(&((a+=b)+=c)==&a && a.value==7);CHECK(b.value==2 && c.value==4);
}
void test_1(){
Meter a(3);a+=a;CHECK(a.value==6);
}
void test_2(){
Meter a(3);a+=Meter(-7);CHECK(a.value==-4);
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
        default:return 2;
        }
        if(mastery_memory::live!=before)throw std::runtime_error("Unreleased allocations after the named check");
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"non-standard exception";return 1;}
}
