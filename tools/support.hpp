#pragma once
#include <stdexcept>
#include <string>
#include <utility>
#include <cstddef>
#include <new>
namespace mastery_memory {
    extern long fail_after;
    extern long live;
}
template<class T> T& mastery_alias(T& value) { return value; }
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(std::string("CHECK failed: ") + #__VA_ARGS__); } while (false)
template<class E, class F> void expect_throw(F&& fn) {
    bool caught = false;
    try { fn(); } catch (const E&) { caught = true; }
    CHECK(caught);
}
// A copyable, default-constructible user type used to detect live-object leaks
// and to inject exceptions into copies/assignments. It deliberately has no <.
struct Tracked {
    inline static int alive = 0;
    inline static int copies_before_throw = -1;
    int value = 0;
    static void checkpoint() {
        if (copies_before_throw == 0) throw std::runtime_error("injected copy failure");
        if (copies_before_throw > 0) --copies_before_throw;
    }
    explicit Tracked(int v=0):value(v) { ++alive; }
    Tracked(const Tracked& other):value(other.value) { checkpoint(); ++alive; }
    Tracked& operator=(const Tracked& other) { checkpoint(); value=other.value; return *this; }
    ~Tracked() { --alive; }
    friend bool operator==(const Tracked& a,const Tracked& b) { return a.value==b.value; }
    friend bool operator!=(const Tracked& a,const Tracked& b) { return !(a==b); }
    friend std::ostream& operator<<(std::ostream& out,const Tracked& v) { return out << v.value; }
};
