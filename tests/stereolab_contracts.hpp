#pragma once
#include <cstddef>
#include <iosfwd>
// Declarations only: used by the contract audit, never a student implementation.
class StereoSample {
public:
    StereoSample(double=0,double=0);
    double left()const; double right()const;
    StereoSample operator+(const StereoSample&)const;
    StereoSample operator-(const StereoSample&)const;
    StereoSample operator-()const;
    StereoSample& operator+=(const StereoSample&);
    StereoSample& operator-=(const StereoSample&);
    StereoSample operator*(double)const;
    bool operator==(const StereoSample&)const;
    bool operator!=(const StereoSample&)const;
    double& operator[](std::size_t);
    const double& operator[](std::size_t)const;
};
StereoSample operator*(double,const StereoSample&);
std::ostream& operator<<(std::ostream&,const StereoSample&);
std::istream& operator>>(std::istream&,StereoSample&);
class ChannelMix {
public:
    ChannelMix(double=1,double=0,double=0,double=1);
    StereoSample operator()(const StereoSample&)const;
    ChannelMix operator*(const ChannelMix&)const;
    bool operator==(const ChannelMix&)const;
    bool operator!=(const ChannelMix&)const;
};
std::ostream& operator<<(std::ostream&,const ChannelMix&);
std::istream& operator>>(std::istream&,ChannelMix&);
class AudioBlock {
public:
    AudioBlock();
    std::size_t size()const; bool empty()const; bool full()const;
    bool append(const StereoSample&);
    StereoSample& operator[](std::size_t);
    const StereoSample& operator[](std::size_t)const;
    AudioBlock operator()(const ChannelMix&)const;
    double average_power()const;
};
AudioBlock apply_filter(const AudioBlock&,const ChannelMix&);
AudioBlock apply_chain(const AudioBlock&,const ChannelMix&,const ChannelMix&);
bool approximately_same(const AudioBlock&,const AudioBlock&,double);
