#include "solution.hpp"
#include <iostream>
#include <exception>
int main(){try{const int code=run_stereolab(std::cin,std::cout);if(code)std::cerr<<"invalid input\n";return code;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
