# d4-p05 · const_cast

const int x=4; int* p=const_cast<int*>(&x); *p=6; std::cout<<x;
