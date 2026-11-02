#include "solution.hpp"
#include "StereoSample.hpp"
#include "ChannelMix.hpp"
#include "AudioBlock.hpp"
#include "StereoIO.hpp"
#include "StereoPipeline.hpp"
#include <iomanip>
#include <stdexcept>
int run_stereolab(std::istream& in,std::ostream& out){
    int count=0;if(!(in>>count))return 1;
    if(count<0||count>4)throw std::out_of_range("count");
    AudioBlock input;
    for(int i=0;i<count;++i){StereoSample sample;if(!(in>>sample))return 1;input.append(sample);}
    ChannelMix first,second;if(!(in>>first>>second))return 1;
    const auto output=apply_chain(input,first,second);
    out<<std::setprecision(17)<<"count="<<count<<"\ninput_power="<<input.average_power()<<"\noutput_power="<<output.average_power();
    if(output.empty())out<<"\nfirst=none\nlast=none\n";
    else out<<"\nfirst="<<output[0]<<"\nlast="<<output[output.size()-1]<<'\n';
    return 0;
}
