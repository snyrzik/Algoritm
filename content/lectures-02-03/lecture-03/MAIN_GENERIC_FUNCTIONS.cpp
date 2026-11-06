// Local tests for Lecture 3, project 1.
// Implement GenericAlgorithms.h without copying these tests into the solution.
// Contract:
// template<typename T> T maximum(T a, T b);
// template<typename T> void swap_values(T& a, T& b);
// template<typename T> T minimum_of_three(T a, T b, T c);
// template<typename T> std::size_t index_of_min(const T*, std::size_t);
// Full specialization maximum<const char*>: compare strings using strcmp.
// Ordinary overload const char* minimum_value(const char*, const char*).

#include "GenericAlgorithms.h"
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>

struct Record {
    int id;
    std::string name;
};

int main() {
    static_assert(std::is_same<decltype(maximum(1, 2)), int>::value,
                  "maximum<int> must return int");
    static_assert(std::is_same<decltype(maximum(1.0, 2.0)), double>::value,
                  "maximum<double> must return double");

    assert(maximum(5, 8) == 8);
    assert(std::fabs(maximum(4.5, 1.0) - 4.5) < 1e-12);
    assert(maximum('a', 'z') == 'z');
    assert(std::fabs(maximum<double>(2, 3.5) - 3.5) < 1e-12);

    int left = 10;
    int right = 20;
    swap_values(left, right);
    assert(left == 20 && right == 10);
    swap_values(left, left);
    assert(left == 20);

    Record first{1, "first"};
    Record second{2, "second"};
    swap_values(first, second);
    assert(first.id == 2 && first.name == "second");
    assert(second.id == 1 && second.name == "first");

    assert(minimum_of_three(3, 1, 5) == 1);
    assert(minimum_of_three(2, 2, 5) == 2);
    assert(minimum_of_three(4, 4, 4) == 4);
    assert(minimum_of_three(-1, 7, -1) == -1);

    int numbers[] = {9, -2, 7, -2, 4};
    assert(index_of_min(numbers, 5) == 1); // FIRST occurrence
    double decimals[] = {2.5, -0.1, 8.0};
    assert(index_of_min(decimals, 3) == 1);

    bool threw = false;
    try {
        (void)index_of_min(static_cast<const int*>(nullptr), 0);
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    assert(threw);

    threw = false;
    try {
        (void)index_of_min(numbers, 0);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw);

    const char a[] = "zebra";
    const char b[] = "apple";
    const char* a_ptr = a;
    const char* b_ptr = b;
    assert(std::strcmp(maximum(a_ptr, b_ptr), "zebra") == 0);
    assert(std::strcmp(maximum<const char*>(a_ptr, b_ptr), "zebra") == 0);
    assert(std::strcmp(minimum_value(a_ptr, b_ptr), "apple") == 0);

    const std::string s1("Ant");
    const std::string s2("Zebra");
    assert(maximum(s1, s2) == s2);

    std::cout << "Lecture 3: generic functions checks passed\n";
}
