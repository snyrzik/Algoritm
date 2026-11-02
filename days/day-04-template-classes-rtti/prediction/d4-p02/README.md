# d4-p02 · Неудачный cast

struct B{virtual ~B()=default;}; struct D:B{}; B b; std::cout<<(dynamic_cast<D*>(&b)==nullptr);
