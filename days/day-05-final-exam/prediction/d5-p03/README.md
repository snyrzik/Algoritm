# d5-p03 · Сбой потока

std::istringstream s("4 x"); int a=0,b=7; s>>a>>b; std::cout<<a<<":"<<s.fail()<<":"<<s.eof();
