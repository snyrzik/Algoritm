# d1-p05 · Порядок жизни

struct X{X(){std::cout<<"C";} ~X(){std::cout<<"D";}}; {X a; {X b;} std::cout<<"|";}
