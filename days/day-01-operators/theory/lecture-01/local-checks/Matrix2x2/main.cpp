// Проверочный main для проекта Matrix2x2.
// Реализацию Matrix2x2 и Point2D напиши самостоятельно.
#include "Matrix2x2.hpp"
#include "Point2D.hpp"

#include <cassert>
#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>

int main() {
    const Matrix2x2 a(1.0, 2.0, 3.0, 4.0);
    const Matrix2x2 b(2.0, 0.0, 1.0, 3.0);

    assert(a(0, 0) == 1.0);
    assert(a(1, 1) == 4.0);
    assert((a + b) == Matrix2x2(3.0, 2.0, 4.0, 7.0));
    assert((a - b) == Matrix2x2(-1.0, 2.0, 2.0, 1.0));
    assert((-a) == Matrix2x2(-1.0, -2.0, -3.0, -4.0));
    assert((a * b) == Matrix2x2(4.0, 6.0, 10.0, 12.0));
    assert((b * a) == Matrix2x2(2.0, 4.0, 10.0, 14.0));
    assert((a * 2.0) == Matrix2x2(2.0, 4.0, 6.0, 8.0));
    assert((2.0 * a) == Matrix2x2(2.0, 4.0, 6.0, 8.0));
    assert(a != b);

    Matrix2x2 mutable_matrix = a;
    mutable_matrix(0, 1) = 9.0;
    assert(mutable_matrix(0, 1) == 9.0);
    mutable_matrix += b;
    assert(mutable_matrix == Matrix2x2(3.0, 9.0, 4.0, 7.0));

    bool bad_index = false;
    try {
        (void)a(2, 0);
    } catch (const std::out_of_range&) {
        bad_index = true;
    }
    assert(bad_index);

    std::ostringstream output;
    output << a;
    assert(output.str() == "[[1,2],[3,4]]");

    Matrix2x2 parsed;
    std::istringstream good_input("[[5,6],[7,8]]");
    good_input >> parsed;
    assert(!good_input.fail());
    assert(parsed == Matrix2x2(5.0, 6.0, 7.0, 8.0));

    const Matrix2x2 before = parsed;
    std::istringstream bad_input("[[1,2],[3,x]]");
    bad_input >> parsed;
    assert(bad_input.fail());
    assert(parsed == before);

    const Point2D point{2.0, 3.0};
    const Point2D transformed = transform(a, point);
    assert(std::abs(transformed.x - 8.0) < 1e-12);
    assert(std::abs(transformed.y - 18.0) < 1e-12);

    std::cout << "Matrix2x2: основные проверки пройдены.\n";
}
