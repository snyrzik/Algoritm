// Проверочный main для проекта DynamicVector.
// Сам класс и triangle_area реализуй самостоятельно.
#include "DynamicVector.hpp"

#include <cassert>
#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>

int main() {
    DynamicVector a(2, 0.0);
    a[0] = 3.0;
    a[1] = 0.0;

    DynamicVector b(2, 0.0);
    b[0] = 0.0;
    b[1] = 4.0;

    assert(a.size() == 2);
    assert((a + b)[0] == 3.0);
    assert((a + b)[1] == 4.0);
    assert((a - b)[1] == -4.0);
    assert(std::abs(a * b) < 1e-12); // Скалярное произведение
    assert((2.0 * a)[0] == 6.0);
    assert((b * 2.0)[1] == 8.0);
    assert((a / 2.0)[0] == 1.5);
    assert(a != b);

    DynamicVector copy = a;
    copy[0] = 99.0;
    assert(a[0] == 3.0); // Независимость копий
    copy = a;
    copy = copy;          // Самоприсваивание
    assert(copy == a);

    a += b;
    assert(a[0] == 3.0 && a[1] == 4.0);

    const DynamicVector& const_view = a;
    assert(const_view[1] == 4.0);

    bool bad_index = false;
    try {
        (void)const_view[2];
    } catch (const std::out_of_range&) {
        bad_index = true;
    }
    assert(bad_index);

    bool bad_size = false;
    try {
        DynamicVector different(3, 1.0);
        (void)(a + different);
    } catch (const std::invalid_argument&) {
        bad_size = true;
    }
    assert(bad_size);

    const DynamicVector side_a = a; // (3,4)
    DynamicVector side_b(2, 0.0);
    side_b[1] = 4.0;               // (0,4)
    assert(std::abs(triangle_area(side_a, side_b) - 6.0) < 1e-12);

    std::ostringstream output;
    output << a;
    assert(!output.str().empty());

    std::cout << "DynamicVector: основные проверки пройдены.\n";
}
