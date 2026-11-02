# d5-p01 · Диагностика копий

struct X{int* p;}; int n=3; X a{&n}; X b=a; *b.p=9; std::cout<<*a.p;
