#pragma once
#include "StereoSample.hpp"
#include "ChannelMix.hpp"
#include "AudioBlock.hpp"
#include <cmath>
#include <stdexcept>
inline AudioBlock apply_filter(const AudioBlock& input,const ChannelMix& mix){return input(mix);}
inline AudioBlock apply_chain(const AudioBlock& input,const ChannelMix& first,const ChannelMix& second){return apply_filter(input,second*first);}
inline bool approximately_same(const AudioBlock& a,const AudioBlock& b,double epsilon){
    if(epsilon<0)throw std::invalid_argument("epsilon");
    if(a.size()!=b.size())return false;
    for(std::size_t i=0;i<a.size();++i){
        if(std::abs(a[i].left()-b[i].left())>epsilon || std::abs(a[i].right()-b[i].right())>epsilon)return false;
    }
    return true;
}
