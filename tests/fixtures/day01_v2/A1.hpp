#pragma once
#include <cstddef>
#include <cmath>
#include <stdexcept>
#include <ostream>
// Test infrastructure only. Never served, imported into the app, or seeded
// into the real learner profile. Used to prove that the grader is operational.
class StereoSample {
    double left_,right_;
public:
    StereoSample(double l=0,double r=0):left_(l),right_(r){}
    double left()const{return left_;}double right()const{return right_;}
    double& operator[](std::size_t i){if(i>=2)throw std::out_of_range("channel");return i?right_:left_;}
    const double& operator[](std::size_t i)const{if(i>=2)throw std::out_of_range("channel");return i?right_:left_;}
    StereoSample& operator+=(const StereoSample& b){left_+=b.left_;right_+=b.right_;return *this;}
    StereoSample& operator-=(const StereoSample& b){left_-=b.left_;right_-=b.right_;return *this;}
    StereoSample operator+(const StereoSample& b)const{auto result=*this;result+=b;return result;}
    StereoSample operator-(const StereoSample& b)const{auto result=*this;result-=b;return result;}
    StereoSample operator-()const{return StereoSample(-left_,-right_);}
    StereoSample operator*(double factor)const{return StereoSample(left_*factor,right_*factor);}
    friend StereoSample operator*(double factor,const StereoSample& sample){return sample*factor;}
    bool operator==(const StereoSample& b)const{return std::abs(left_-b.left_)<=1e-9 && std::abs(right_-b.right_)<=1e-9;}
    bool operator!=(const StereoSample& b)const{return !(*this==b);}
    friend std::ostream& operator<<(std::ostream& out,const StereoSample& s){return out<<'('<<s.left_<<','<<s.right_<<')';}
};
