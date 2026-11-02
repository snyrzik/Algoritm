#pragma once
#include "StereoSample.hpp"
#include "ChannelMix.hpp"
#include "AudioBlock.hpp"
#include <istream>
inline std::istream& operator>>(std::istream& in,StereoSample& value){
    char open=0,comma=0,close=0;double left=0,right=0;
    if(in>>open>>left>>comma>>right>>close){if(open=='(' && comma==',' && close==')')value=StereoSample(left,right);else in.setstate(std::ios::failbit);}return in;
}
inline std::istream& operator>>(std::istream& in,ChannelMix& value){
    char p=0,q=0,r=0,s=0,t=0,u=0,v=0,w=0,z=0;double a=0,b=0,c=0,d=0;
    if(in>>p>>q>>a>>r>>b>>s>>t>>u>>c>>v>>d>>w>>z){if(p=='['&&q=='['&&r==','&&s==']'&&t==','&&u=='['&&v==','&&w==']'&&z==']')value=ChannelMix(a,b,c,d);else in.setstate(std::ios::failbit);}return in;
}
