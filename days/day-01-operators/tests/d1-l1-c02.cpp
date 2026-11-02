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

static_assert(std::is_member_function_pointer_v<decltype(mastery_check::duration_read)>);
static_assert(std::is_invocable_v<decltype(mastery_check::duration_read),const Duration&>);
static_assert(std::is_integral_v<std::remove_cv_t<std::remove_reference_t<std::invoke_result_t<decltype(mastery_check::duration_read),const Duration&>>>>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()+std::declval<const Duration&>()),Duration>);
static_assert(std::is_same_v<decltype(std::declval<Duration&>()+=std::declval<const Duration&>()),Duration&>);
static_assert(std::is_same_v<decltype(-std::declval<const Duration&>()),Duration>);
static_assert(std::is_same_v<decltype(++std::declval<Duration&>()),Duration&>);
static_assert(std::is_same_v<decltype(std::declval<Duration&>()++),Duration>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()==std::declval<const Duration&>()),bool>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()!=std::declval<const Duration&>()),bool>);

void test_0() {
const Duration zero(0),negative(-7),positive(61); CHECK(std::invoke(mastery_check::duration_read,zero)==0); CHECK(std::invoke(mastery_check::duration_read,negative)==-7); CHECK(std::invoke(mastery_check::duration_read,positive)==61);
}
void test_1() {
const Duration a(59),b(61); const Duration c=a+b; CHECK(std::invoke(mastery_check::duration_read,c)==120); CHECK(std::invoke(mastery_check::duration_read,a)==59 && std::invoke(mastery_check::duration_read,b)==61);
}
void test_2() {
Duration a(59); const Duration b(61); CHECK(&((a+=b)+=Duration(3))==&a); CHECK(std::invoke(mastery_check::duration_read,a)==123 && std::invoke(mastery_check::duration_read,b)==61);
}
void test_3() {
CHECK(std::invoke(mastery_check::duration_read,Duration(-15)+Duration(7))==-8); CHECK(std::invoke(mastery_check::duration_read,Duration(-15)+Duration(-7))==-22); CHECK(std::invoke(mastery_check::duration_read,Duration(7)+Duration(-7))==0);
}
void test_4() {
const Duration a(-12); CHECK(std::invoke(mastery_check::duration_read,-a)==12); CHECK(std::invoke(mastery_check::duration_read,a)==-12); CHECK(std::invoke(mastery_check::duration_read,-Duration(0))==0);
}
void test_5() {
const Duration a(17),b(17),c(-17); CHECK(a==b && !(a!=b)); CHECK(a!=c && !(a==c)); CHECK(a==a);
}
void test_6() {
Duration value(7); Duration& result=++value; CHECK(&result==&value); CHECK(std::invoke(mastery_check::duration_read,value)==8 && std::invoke(mastery_check::duration_read,result)==8);
}
void test_7() {
Duration value(8); Duration before=value++; CHECK(std::invoke(mastery_check::duration_read,before)==8 && std::invoke(mastery_check::duration_read,value)==9); ++value; CHECK(std::invoke(mastery_check::duration_read,before)==8);
}
void test_8() {
Duration value(7); Duration first=++value; Duration second=value++; CHECK(std::invoke(mastery_check::duration_read,first)==8); CHECK(std::invoke(mastery_check::duration_read,second)==8); CHECK(std::invoke(mastery_check::duration_read,value)==9);
}
void test_9() {
Duration value(-1); CHECK(&(value+=value)==&value); CHECK(std::invoke(mastery_check::duration_read,value)==-2); ++value; value++; CHECK(std::invoke(mastery_check::duration_read,value)==0);
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
        default:return 2;
        }
        CHECK(mastery_memory::live==before);
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"unexpected exception";return 1;}
}
