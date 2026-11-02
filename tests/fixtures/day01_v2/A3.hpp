#pragma once
#include "StereoSample.hpp"
#include "ChannelMix.hpp"
#include <cstddef>
#include <stdexcept>
class AudioBlock {
    StereoSample samples_[4];
    std::size_t used_=0;
public:
    std::size_t size()const{return used_;}bool empty()const{return used_==0;}bool full()const{return used_==4;}
    bool append(const StereoSample& sample){if(full())return false;samples_[used_]=sample;++used_;return true;}
    StereoSample& operator[](std::size_t i){if(i>=used_)throw std::out_of_range("sample");return samples_[i];}
    const StereoSample& operator[](std::size_t i)const{if(i>=used_)throw std::out_of_range("sample");return samples_[i];}
    AudioBlock operator()(const ChannelMix& mix)const{AudioBlock out;for(std::size_t i=0;i<used_;++i)out.append(mix(samples_[i]));return out;}
    double average_power()const{if(empty())return 0;double total=0;for(std::size_t i=0;i<used_;++i){const auto& s=samples_[i];total+=(s.left()*s.left()+s.right()*s.right())/2;}return total/static_cast<double>(used_);}
};
