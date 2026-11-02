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

static_assert(std::is_member_function_pointer_v<decltype(mastery_check::score_read)>, "Bind your reading METHOD in test_adapter.hpp");
static_assert(std::is_member_function_pointer_v<decltype(mastery_check::score_add)>, "Bind your modifying METHOD in test_adapter.hpp");
static_assert(std::is_invocable_v<decltype(mastery_check::score_read),const ScoreCounter&>, "Reading must work on const objects");
static_assert(std::is_integral_v<std::remove_cv_t<std::remove_reference_t<std::invoke_result_t<decltype(mastery_check::score_read),const ScoreCounter&>>>>);
static_assert(std::is_same_v<std::invoke_result_t<decltype(mastery_check::score_add),ScoreCounter&,int>,ScoreCounter&>, "Chain must return ScoreCounter&");
using HigherScoreSignature = bool (*)(const ScoreCounter&,const ScoreCounter&);
static_assert(std::is_same_v<decltype(static_cast<HigherScoreSignature>(&higher_score)),HigherScoreSignature>, "Compare without copying the parameters");

void test_0() {
const ScoreCounter zero; const ScoreCounter other(17); CHECK(std::invoke(mastery_check::score_read,zero)==0); CHECK(std::invoke(mastery_check::score_read,other)==17);
}
void test_1() {
ScoreCounter s(10); std::invoke(mastery_check::score_add,s,7); CHECK(std::invoke(mastery_check::score_read,s)==17); std::invoke(mastery_check::score_add,s,-25); CHECK(std::invoke(mastery_check::score_read,s)==-8); std::invoke(mastery_check::score_add,s,0); CHECK(std::invoke(mastery_check::score_read,s)==-8);
}
void test_2() {
ScoreCounter s(3); auto& first=std::invoke(mastery_check::score_add,s,2); CHECK(&first==&s); auto& second=std::invoke(mastery_check::score_add,first,4); CHECK(&second==&s && std::invoke(mastery_check::score_read,s)==9);
}
void test_3() {
const ScoreCounter a(12),b(5),c(12); CHECK(higher_score(a,b)); CHECK(!higher_score(b,a)); CHECK(!higher_score(a,c)); CHECK(std::invoke(mastery_check::score_read,a)==12 && std::invoke(mastery_check::score_read,b)==5);
}
void test_4() {
const ScoreCounter a(-2),b(-10); CHECK(higher_score(a,b)); CHECK(!higher_score(b,a));
}
void test_5() {
ScoreCounter a(20); ScoreCounter b(a); std::invoke(mastery_check::score_add,b,15); CHECK(std::invoke(mastery_check::score_read,a)==20 && std::invoke(mastery_check::score_read,b)==35);
}
void test_6() {
ScoreCounter* copy=nullptr; {const ScoreCounter original(44); copy=new ScoreCounter(original);} CHECK(std::invoke(mastery_check::score_read,*copy)==44); delete copy;
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
        default:return 2;
        }
        CHECK(mastery_memory::live==before);
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what();return 1;}
    catch(...){std::cerr<<"unexpected exception";return 1;}
}
