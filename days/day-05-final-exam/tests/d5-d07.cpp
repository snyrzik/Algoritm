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

void test_0() {
char* p=new char[4]{char(97),char(98),char(99),0}; replace_copy(p,p); CHECK(std::strcmp(p,"abc")==0); delete[] p;
}
void test_1() {
char* p=new char[2]{char(97),0}; mastery_memory::fail_after=0; bool caught=false; try{replace_copy(p,"bbb");}catch(const std::bad_alloc&){caught=true;} mastery_memory::fail_after=-1; CHECK(caught && p[0]==char(97)); delete[] p;
}
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    try {
        const auto live_before = mastery_memory::live;
        switch (std::stoi(argv[1])) {
case 0: test_0(); break;
case 1: test_1(); break;
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
