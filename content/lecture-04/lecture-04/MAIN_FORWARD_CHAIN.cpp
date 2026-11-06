// Лекция 4, проект 1. Скомпилировать со своим forward_chain.hpp.
// Это обычный локальный main, не готовое решение класса.
#include "forward_chain.hpp"

#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>

int main() {
    ForwardChain<int> chain;
    assert(chain.empty());
    assert(chain.size() == 0U);
    assert(!chain.contains(99));
    assert(!chain.erase_first(99));

    bool empty_error = false;
    try {
        (void)chain.pop_front();
    } catch (const std::out_of_range&) {
        empty_error = true;
    }
    assert(empty_error);

    chain.push_front(30);
    chain.push_front(20);
    chain.push_front(10);
    assert(chain.size() == 3U);
    assert(chain.front() == 10);
    assert(chain.contains(20));
    assert(!chain.contains(5));

    const ForwardChain<int>& readonly = chain;
    assert(readonly.front() == 10);
    assert(readonly.contains(30));

    assert(chain.erase_first(20));
    assert(chain.size() == 2U);
    assert(!chain.contains(20));
    assert(chain.pop_front() == 10);
    assert(chain.pop_front() == 30);
    assert(chain.empty());

    chain.push_front(1);
    chain.push_front(2);
    chain.push_front(3); // 3, 2, 1
    chain.reverse();    // 1, 2, 3
    assert(chain.pop_front() == 1);
    assert(chain.pop_front() == 2);
    assert(chain.pop_front() == 3);
    assert(chain.empty());

    ForwardChain<std::string> words;
    words.push_front("one");
    words.push_front("two");
    ForwardChain<std::string> copy(words);
    assert(copy.size() == 2U);
    assert(copy.front() == "two");
    words.pop_front();
    assert(copy.front() == "two"); // Копии независимы

    ForwardChain<std::string> assigned;
    assigned.push_front("old");
    assigned = copy;
    assert(assigned.size() == 2U);
    assert(assigned.pop_front() == "two");
    assert(assigned.pop_front() == "one");

    copy = copy; // Самоприсваивание
    assert(copy.size() == 2U);
    assert(copy.front() == "two");

    copy.clear();
    copy.clear();
    assert(copy.empty());

    std::cout << "ForwardChain: basic checks passed\n";
}
