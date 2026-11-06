// Local C++17 checks for the applied part of Lecture 3, project 3.
// Implement PostfixEvaluator.h with the external function:
//   double evaluate_postfix(const std::string& expression);
// Use your own LinkedStack<double> as the value stack.
// Tokens are separated by whitespace. The operators + - * / are standalone
// tokens; signed numeric literals such as -3 are valid operands.
// Invalid input or division by zero throws std::invalid_argument.

#include "PostfixEvaluator.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>

bool near(double actual, double expected) {
    return std::fabs(actual - expected) < 1e-10;
}

bool invalid(const std::string& expression) {
    try {
        (void)evaluate_postfix(expression);
    } catch (const std::invalid_argument&) {
        return true;
    }
    return false;
}

int main() {
    assert(near(evaluate_postfix("3 4 +"), 7.0));
    assert(near(evaluate_postfix("5 1 2 + 4 * + 3 -"), 14.0));
    assert(near(evaluate_postfix("2 3 4 * +"), 14.0));
    assert(near(evaluate_postfix("10 2 /"), 5.0));
    assert(near(evaluate_postfix("7"), 7.0));
    assert(near(evaluate_postfix("-3 2 *"), -6.0));
    assert(near(evaluate_postfix("1.5 2 +"), 3.5));

    assert(invalid(""));
    assert(invalid("1 +"));
    assert(invalid("1 2"));
    assert(invalid("1 0 /"));
    assert(invalid("2 unknown +"));
    assert(invalid("+"));

    std::cout << "Lecture 3: postfix evaluator checks passed\n";
}
