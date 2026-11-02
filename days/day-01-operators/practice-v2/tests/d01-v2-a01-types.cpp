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
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>().left()),double> && std::is_same_v<decltype(std::declval<const StereoSample&>().right()),double>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()[0]),double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()[0]),const double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()+std::declval<const StereoSample&>()),StereoSample>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()+=std::declval<const StereoSample&>()),StereoSample&> && std::is_same_v<decltype(std::declval<StereoSample&>()-=std::declval<const StereoSample&>()),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const StereoSample&>()),std::ostream&>);
int main(){return 0;}
