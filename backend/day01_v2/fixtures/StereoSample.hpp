#pragma once
#include <cstddef>
#include <cmath>
#include <ostream>
#include <stdexcept>
// Minimal test dependency for autonomous A2/A3. Deliberately lacks the A1
// arithmetic and compound operators, so it is not a complete A1 solution.
class StereoSample {
    double channels_[2];
public:
    StereoSample(double left=0,double right=0):channels_{left,right}{}
    double left()const{return channels_[0];}
    double right()const{return channels_[1];}
    double& operator[](std::size_t i){if(i>=2)throw std::out_of_range("channel");return channels_[i];}
    const double& operator[](std::size_t i)const{if(i>=2)throw std::out_of_range("channel");return channels_[i];}
    bool operator==(const StereoSample& b)const{return std::abs(left()-b.left())<=1e-9 && std::abs(right()-b.right())<=1e-9;}
    bool operator!=(const StereoSample& b)const{return !(*this==b);}
    friend std::ostream& operator<<(std::ostream& out,const StereoSample& s){return out<<'('<<s.left()<<','<<s.right()<<')';}
};
