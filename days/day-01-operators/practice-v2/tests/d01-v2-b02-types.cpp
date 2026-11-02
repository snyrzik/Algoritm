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
using F=AudioBlock(*)(const AudioBlock&,const ChannelMix&);using Chain=AudioBlock(*)(const AudioBlock&,const ChannelMix&,const ChannelMix&);using Same=bool(*)(const AudioBlock&,const AudioBlock&,double);
static_assert(std::is_same_v<decltype(static_cast<F>(&apply_filter)),F> && std::is_same_v<decltype(static_cast<Chain>(&apply_chain)),Chain> && std::is_same_v<decltype(static_cast<Same>(&approximately_same)),Same>);
int main(){return 0;}
