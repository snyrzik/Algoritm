// Лекция 4, проект 3. Скомпилировать со своим collection_operations.hpp.
// В этом проекте использование контейнеров STL является частью задания.
#include "collection_operations.hpp"

#include <cassert>
#include <deque>
#include <iostream>
#include <list>
#include <vector>

int main() {
    using collection_lab::insert_marker_before_each_even;
    using collection_lab::merge_sorted;
    using collection_lab::remove_negative;
    using collection_lab::rotate_left;

    std::vector<int> values{1, 2, 4, 5};
    insert_marker_before_each_even(values, 8);
    assert((values == std::vector<int>{1, 8, 2, 8, 4, 5}));

    // Маркер тоже чётный: нельзя повторно обрабатывать только что вставленные 8.
    std::vector<int> mixed{-2, 0, 3, 6};
    insert_marker_before_each_even(mixed, 8);
    assert((mixed == std::vector<int>{8, -2, 8, 0, 3, 8, 6}));

    std::vector<int> no_even{1, 3, 5};
    insert_marker_before_each_even(no_even, 7);
    assert((no_even == std::vector<int>{1, 3, 5}));

    std::list<int> temperatures{5, -2, 0, -4, 7, -1};
    remove_negative(temperatures);
    assert((temperatures == std::list<int>{5, 0, 7}));

    std::list<int> all_negative{-1, -2};
    remove_negative(all_negative);
    assert(all_negative.empty());

    std::deque<int> queue{10, 20, 30, 40};
    rotate_left(queue, 6U); // 6 mod 4 == 2
    assert((queue == std::deque<int>{30, 40, 10, 20}));
    rotate_left(queue, 0U);
    assert((queue == std::deque<int>{30, 40, 10, 20}));

    std::deque<int> empty;
    rotate_left(empty, 1000U);
    assert(empty.empty());

    const std::list<int> first{1, 3, 5};
    const std::list<int> second{2, 3, 4, 6};
    std::list<int> merged = merge_sorted(first, second);
    assert((merged == std::list<int>{1, 2, 3, 3, 4, 5, 6}));
    assert((first == std::list<int>{1, 3, 5}));
    assert((second == std::list<int>{2, 3, 4, 6}));

    std::cout << "CollectionLab: basic checks passed\n";
}
