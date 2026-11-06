// Local tests for Lecture 3, project 2.
// Implement the complete template in FixedStack.h.
// Template form: FixedStack<T, int Capacity = 256> (Capacity > 0).
// Required API:
//   bool push(const T& value);
//   bool pop(T& out);
//   bool peek(T& out) const;
//   std::size_t size() const;
//   bool empty() const;
//   bool full() const;
// Failed pop/peek must not change 'out'.

#include "FixedStack.h"
#include <cassert>
#include <cstddef>
#include <iostream>
#include <string>

int main() {
    FixedStack<int, 3> stack;
    assert(stack.empty());
    assert(!stack.full());
    assert(stack.size() == 0);

    int output = 999;
    assert(!stack.pop(output) && output == 999);
    assert(!stack.peek(output) && output == 999);

    assert(stack.push(10));
    assert(stack.push(20));
    assert(stack.push(30));
    assert(stack.full());
    assert(stack.size() == 3);
    assert(!stack.push(40));
    assert(stack.size() == 3);

    const FixedStack<int, 3>& const_stack = stack;
    assert(const_stack.peek(output));
    assert(output == 30);
    assert(const_stack.size() == 3);

    assert(stack.pop(output) && output == 30);
    assert(stack.pop(output) && output == 20);
    assert(stack.push(50));
    assert(stack.pop(output) && output == 50);
    assert(stack.pop(output) && output == 10);
    assert(stack.empty());
    output = 123;
    assert(!stack.pop(output) && output == 123);

    FixedStack<std::string, 2> strings;
    assert(strings.push("one"));
    assert(strings.push("two"));
    std::string word;
    assert(strings.pop(word) && word == "two");
    assert(strings.pop(word) && word == "one");
    assert(strings.empty());

    FixedStack<double> defaults;
    assert(defaults.push(2.5));
    double decimal = 0;
    assert(defaults.pop(decimal) && decimal == 2.5);

    std::cout << "Lecture 3: fixed stack checks passed\n";
}
