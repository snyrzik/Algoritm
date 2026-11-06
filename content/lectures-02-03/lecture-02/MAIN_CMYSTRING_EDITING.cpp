// Local C++17 checks for the Lecture 2 CMyString extension.
// Implement the class yourself in CMyString.h, reusing Lecture 1.
// Required new methods: erase(position,count),
// replace_range(position,count,const char*).
// Compile WITHOUT -DNDEBUG: checks use assert.

#include "CMyString.h"
#include <cassert>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>

bool equals(const CMyString& actual, const char* expected) {
    return std::strcmp(actual.c_str(), expected) == 0 &&
           actual.size() == std::strlen(expected);
}

int main() {
    CMyString text("HelloWorld");
    const char* original_buffer = text.c_str();
    text.erase(5, 3);
    assert(text.c_str() == original_buffer); // erase does not reallocate
    assert(equals(text, "Hellold"));
    text.erase(5, 0);
    assert(equals(text, "Hellold"));
    text.erase(text.size(), 0);
    assert(equals(text, "Hellold"));
    text.erase(0, text.size());
    assert(equals(text, ""));

    CMyString empty("");
    empty.erase(0, 0);
    assert(equals(empty, ""));

    CMyString range("abcdef");
    bool threw = false;
    try {
        range.erase(4, 3);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && equals(range, "abcdef"));

    threw = false;
    try {
        range.erase(7, 0);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && equals(range, "abcdef"));

    threw = false;
    try {
        range.erase(1, (std::numeric_limits<std::size_t>::max)());
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && equals(range, "abcdef"));

    CMyString replacement("ABCDEF");
    replacement.replace_range(1, 2, "xyz");
    assert(equals(replacement, "AxyzDEF"));
    replacement.replace_range(1, 3, "");
    assert(equals(replacement, "ADEF"));
    replacement.replace_range(replacement.size(), 0, "!");
    assert(equals(replacement, "ADEF!"));
    replacement.replace_range(0, replacement.size(), "Z");
    assert(equals(replacement, "Z"));

    CMyString alias("ABCDE");
    alias.replace_range(1, 2, alias.c_str() + 3);
    assert(equals(alias, "ADEDE"));

    CMyString self("mirror");
    self.replace_range(0, 0, self.c_str());
    assert(equals(self, "mirrormirror"));

    CMyString invalid("unchanged");
    threw = false;
    try {
        invalid.replace_range(2, 0, nullptr);
    } catch (const std::invalid_argument&) {
        threw = true;
    }
    assert(threw && equals(invalid, "unchanged"));

    threw = false;
    try {
        invalid.replace_range(7, 3, "X");
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && equals(invalid, "unchanged"));

    threw = false;
    try {
        invalid.replace_range(0, (std::numeric_limits<std::size_t>::max)(), "X");
    } catch (const std::out_of_range&) {
        threw = true;
    }
    assert(threw && equals(invalid, "unchanged"));

    std::cout << "Lecture 2: CMyString editing checks passed\n";
}
