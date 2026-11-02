#pragma once
#include "StereoSample.hpp"
// Minimal A3 dependency: application only, no composition/comparison/output.
// B/C never use this fixture; they compile the learner's A1/A2/A3 sources.
class ChannelMix {
    double a_,b_,c_,d_;
public:
    ChannelMix(double a=1,double b=0,double c=0,double d=1):a_(a),b_(b),c_(c),d_(d){}
    StereoSample operator()(const StereoSample& s)const{return StereoSample(a_*s.left()+b_*s.right(),c_*s.left()+d_*s.right());}
};
