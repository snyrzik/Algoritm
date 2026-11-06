// Local tests for Lecture 3, project 3.
// Implement IStack.h and LinkedStack.h yourself.
// IStack<T> has virtual ~IStack(), push, pop, peek, size.
// LinkedStack<T> must deeply copy its linked nodes.
// Upgrade FixedStack<T, Capacity> to derive from IStack<T>.
// Contract: failed pop/peek leaves the output argument unchanged.

#include "IStack.h"
#include "FixedStack.h"
#include "LinkedStack.h"
#include <cassert>
#include <cstddef>
#include <iostream>
#include <string>
#include <type_traits>

struct NoDefault {
    int value;
    explicit NoDefault(int initial) : value(initial) {}
};

template <typename T>
std::size_t load_two(IStack<T>& stack, const T& first, const T& second) {
    const bool a = stack.push(first);
    const bool b = stack.push(second);
    return static_cast<std::size_t>(a) + static_cast<std::size_t>(b);
}

int main() {
    static_assert(std::has_virtual_destructor<IStack<int>>::value,
                  "IStack<T> needs a virtual destructor");

    LinkedStack<int> stack;
    int output = 999;
    assert(stack.size() == 0);
    assert(!stack.pop(output) && output == 999);
    assert(!stack.peek(output) && output == 999);

    assert(stack.push(10));
    assert(stack.push(20));
    assert(stack.push(30));
    assert(stack.size() == 3);

    LinkedStack<int> copy(stack);
    assert(copy.pop(output) && output == 30);
    assert(copy.pop(output) && output == 20);
    assert(stack.peek(output) && output == 30); // independent copy
    assert(stack.size() == 3);

    LinkedStack<int> assigned;
    assert(assigned.push(777));
    assigned = stack;
    assert(assigned.size() == 3);
    assert(assigned.pop(output) && output == 30);
    assigned = assigned;
    assert(assigned.size() == 2);
    assert(stack.size() == 3);

    LinkedStack<int> empty;
    assigned = empty;
    assert(assigned.size() == 0);
    LinkedStack<int> copy_empty(empty);
    assert(copy_empty.size() == 0);

    IStack<int>& polymorphic = stack;
    assert(load_two(polymorphic, 40, 50) == 2);
    assert(polymorphic.size() == 5);
    assert(polymorphic.pop(output) && output == 50);
    assert(polymorphic.peek(output) && output == 40);

    FixedStack<int, 2> fixed;
    IStack<int>& fixed_base = fixed;
    assert(load_two(fixed_base, 1, 2) == 2);
    assert(!fixed_base.push(3));
    assert(fixed_base.pop(output) && output == 2);

    LinkedStack<std::string> words;
    assert(words.push("first"));
    assert(words.push("second"));
    std::string word;
    assert(words.pop(word) && word == "second");

    LinkedStack<NoDefault> objects;
    assert(objects.push(NoDefault(42)));
    NoDefault result(0);
    assert(objects.pop(result) && result.value == 42);

    IStack<int>* owned = new LinkedStack<int>();
    assert(owned->push(33));
    delete owned; // checks destructor semantics; use sanitizer for leak detection

    std::cout << "Lecture 3: linked stack checks passed\n";
}
