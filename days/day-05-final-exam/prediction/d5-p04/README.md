# d5-p04 · Явная специализация

template<class T> int f(T){return 1;} template<> int f<int>(int){return 7;} std::cout<<f(2)<<f(2.0);
