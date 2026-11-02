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
char* p=new char[5]{char(116),char(101),char(115),char(116),0}; replace_copy(p,p+1); CHECK(std::strcmp(p,"est")==0); delete[] p;
}
void test_1() {
char* p=new char[4]{char(111),char(108),char(100),0}; mastery_memory::fail_after=0; bool caught=false; try{replace_copy(p,"new text");}catch(const std::bad_alloc&){caught=true;} mastery_memory::fail_after=-1; CHECK(caught && std::strcmp(p,"old")==0); delete[] p;
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
