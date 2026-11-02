# d3-p01 · Обычная перегрузка

template<class T> int f(T){return 1;} int f(int){return 2;} std::cout<<f(3)<<f<double>(3);
