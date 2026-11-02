# d2-p04 · Сворачивание стека

struct G{~G(){std::cout<<"D";}}; try{G g;throw std::runtime_error("x");}catch(const std::exception&){std::cout<<"C";}
