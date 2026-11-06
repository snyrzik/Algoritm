// Local checks for the Lecture 3 RTTI checkpoint.
// Implement RttiLab.h yourself. Use a polymorphic Shape base.
// Required API:
//   Rectangle(double width, double height);
//   Circle(double radius);
//   virtual double area() const;
//   bool is_rectangle(const Shape& value);
//   const Rectangle& require_rectangle(const Shape& value);
//   bool is_exact_circle(const Shape& value);
// Invalid negative dimensions should throw std::invalid_argument.
// 'require_rectangle' uses dynamic_cast on a reference and may throw bad_cast.

#include "RttiLab.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <typeinfo>
#include <type_traits>

int main() {
    static_assert(std::has_virtual_destructor<Shape>::value,
                  "Shape needs a virtual destructor");

    Rectangle rectangle(3.0, 4.0);
    Circle circle(2.0);
    const Shape& r = rectangle;
    const Shape& c = circle;

    assert(std::fabs(r.area() - 12.0) < 1e-10);
    assert(std::fabs(c.area() - 12.566370614359172) < 1e-10);
    assert(is_rectangle(r));
    assert(!is_rectangle(c));
    assert(!is_exact_circle(r));
    assert(is_exact_circle(c));
    assert(&require_rectangle(r) == &rectangle);

    bool bad_cast = false;
    try {
        (void)require_rectangle(c);
    } catch (const std::bad_cast&) {
        bad_cast = true;
    }
    assert(bad_cast);

    bool invalid = false;
    try {
        Rectangle wrong(-1.0, 2.0);
        (void)wrong;
    } catch (const std::invalid_argument&) {
        invalid = true;
    }
    assert(invalid);

    std::cout << "Lecture 3: RTTI checkpoint checks passed\n";
}
