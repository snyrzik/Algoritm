# d5-p02 · Перестановка обработчиков

try{throw std::out_of_range("i");}catch(const std::exception&){std::cout<<"base";}catch(const std::out_of_range&){std::cout<<"range";}
