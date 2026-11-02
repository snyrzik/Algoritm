#include <cstddef>
#include <cstdlib>
#include <cstdio>
#include <new>
#include <limits>
namespace mastery_memory {
    long fail_after = -1;
    long live = 0;
    union Header { std::max_align_t alignment; bool array; };
    void* allocate(std::size_t size, bool array) {
        if (fail_after==0) { fail_after=-1; throw std::bad_alloc(); }
        if (fail_after>0) --fail_after;
        if(size > std::numeric_limits<std::size_t>::max()-sizeof(Header)) throw std::bad_alloc();
        void* raw=std::malloc(sizeof(Header)+(size?size:1));
        if(!raw) throw std::bad_alloc();
        auto* base=::new(raw) Header{};
        base->array=array; ++live;
        return base+1;
    }
    void release(void* p, bool array) noexcept {
        if(!p)return;
        auto* base=static_cast<Header*>(p)-1;
        if(base->array!=array){std::fputs("MEMORY: new/delete family mismatch\n",stderr);std::abort();}
        --live; std::free(base);
    }
}
void* operator new(std::size_t n){return mastery_memory::allocate(n,false);}
void* operator new[](std::size_t n){return mastery_memory::allocate(n,true);}
void operator delete(void* p) noexcept{mastery_memory::release(p,false);}
void operator delete[](void* p) noexcept{mastery_memory::release(p,true);}
void operator delete(void* p,std::size_t) noexcept{mastery_memory::release(p,false);}
void operator delete[](void* p,std::size_t) noexcept{mastery_memory::release(p,true);}
