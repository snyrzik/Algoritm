# d4-p04 · Динамический тип

struct B{virtual ~B()=default;}; struct D:B{}; D d; B& b=d; std::cout<<(typeid(b)==typeid(D));
