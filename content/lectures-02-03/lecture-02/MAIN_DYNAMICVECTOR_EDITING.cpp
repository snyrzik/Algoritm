// Local C++17 checks for the Lecture 2 DynamicVector extension.
// Reuse your Lecture 1 DynamicVector implementation.
// Required new methods:
//   void resize(std::size_t new_size, double fill = 0.0);
//   void insert(std::size_t index, double value);
//   void erase(std::size_t index);

#include "DynamicVector.h"
#include <cassert>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <stdexcept>

bool close_to(double actual, double expected) {
    return std::fabs(actual - expected) < 1e-10;
}

int main() {
    DynamicVector values(2, 1.5);
    assert(values.size() == 2);
    values.resize(4, 7.0);
    assert(values.size() == 4);
    assert(close_to(values[0], 1.5));
    assert(close_to(values[1], 1.5));
    assert(close_to(values[2], 7.0));
    assert(close_to(values[3], 7.0));

    values.resize(2, 100.0);
    assert(values.size() == 2);
    assert(close_to(values[1], 1.5));
    values.resize(2, -50.0);
    assert(values.size() == 2 && close_to(values[0], 1.5));

    values.insert(0, 9.0);       // [9,1.5,1.5]
    values.insert(2, 4.0);       // [9,1.5,4,1.5]
    values.insert(values.size(), 8.0); // [9,1.5,4,1.5,8]
    assert(values.size() == 5);
    assert(close_to(values[0], 9.0));
    assert(close_to(values[2], 4.0));
    assert(close_to(values[4], 8.0));

    DynamicVector copy(values);
    copy.erase(1);               // [9,4,1.5,8]
    assert(copy.size() == 4);
    assert(close_to(copy[1], 4.0));
    assert(values.size() == 5);
    assert(close_to(values[1], 1.5));

    const double* original_buffer = &values[0];
    values.erase(0);             // [1.5,4,1.5,8]
    assert(&values[0] == original_buffer); // in-place erase
    values.erase(values.size() - 1); // [1.5,4,1.5]
    assert(values.size() == 3);
    assert(close_to(values[0], 1.5));
    assert(close_to(values[1], 4.0));
    assert(close_to(values[2], 1.5));

    DynamicVector empty(0, 0.0);
    empty.insert(0, 42.0);
    assert(empty.size() == 1 && close_to(empty[0], 42.0));
    empty.erase(0);
    assert(empty.size() == 0);
    empty.resize(3);
    assert(empty.size() == 3);
    assert(close_to(empty[0], 0.0));
    assert(close_to(empty[1], 0.0));
    assert(close_to(empty[2], 0.0));

    bool threw = false;
    try {
        empty.insert(4, 12.0);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && empty.size() == 3 && close_to(empty[0], 0.0));

    threw = false;
    try {
        empty.erase(3);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && empty.size() == 3);

    DynamicVector self(3, 2.0);
    self = self;
    self.insert(self.size(), 5.0);
    assert(self.size() == 4 && close_to(self[3], 5.0));

    std::cout << "Lecture 2: DynamicVector editing checks passed\n";
}
