# d1-p03 · Временный результат

struct V{int n; V operator+=(const V& r){n+=r.n;return *this;}}; V a{1},b{2},c{3}; (a+=b)+=c; std::cout<<a.n;
