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
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>().size()),std::size_t>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>()[0]),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()[0]),const StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>().append(std::declval<const StereoSample&>())),bool>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()(std::declval<const ChannelMix&>())),AudioBlock>);
int main(){return 0;}
