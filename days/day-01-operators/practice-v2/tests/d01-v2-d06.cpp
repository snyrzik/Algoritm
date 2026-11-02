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
static_assert(std::is_same_v<decltype(std::declval<const Measurement&>()==std::declval<const Measurement&>()),bool>);static_assert(std::is_same_v<decltype(std::declval<const Measurement&>()!=std::declval<const Measurement&>()),bool>);
void test_0(){
const Measurement a(1.1),b(1.9);CHECK(!(a==b) && a!=b);
}
void test_1(){
const Measurement a(0),b(0.5e-9),c(2e-9);CHECK(a==b && !(a!=b));CHECK(a!=c && !(a==c));
}
void test_2(){
CHECK(Measurement(0)==Measurement(1e-9));CHECK(Measurement(0)!=Measurement(1.01e-9));
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
