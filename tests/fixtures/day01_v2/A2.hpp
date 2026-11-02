#pragma once
#include "StereoSample.hpp"
#include <cmath>
#include <ostream>
class ChannelMix {
    double a_,b_,c_,d_;
public:
    ChannelMix(double a=1,double b=0,double c=0,double d=1):a_(a),b_(b),c_(c),d_(d){}
    StereoSample operator()(const StereoSample& s)const{return StereoSample(a_*s.left()+b_*s.right(),c_*s.left()+d_*s.right());}
    ChannelMix operator*(const ChannelMix& r)const{return ChannelMix(a_*r.a_+b_*r.c_,a_*r.b_+b_*r.d_,c_*r.a_+d_*r.c_,c_*r.b_+d_*r.d_);}
    bool operator==(const ChannelMix& r)const{return std::abs(a_-r.a_)<=1e-9 && std::abs(b_-r.b_)<=1e-9 && std::abs(c_-r.c_)<=1e-9 && std::abs(d_-r.d_)<=1e-9;}
    bool operator!=(const ChannelMix& r)const{return !(*this==r);}
    friend std::ostream& operator<<(std::ostream& out,const ChannelMix& m){return out<<"[["<<m.a_<<','<<m.b_<<"],["<<m.c_<<','<<m.d_<<"]]";}
};
