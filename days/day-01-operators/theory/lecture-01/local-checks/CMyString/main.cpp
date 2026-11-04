// Проверочный main для проекта CMyString.
// Реализацию класса напиши самостоятельно.
#include "CMyString.hpp"

#include <cassert>
#include <cstring>
#include <iostream>
#include <sstream>
#include <stdexcept>

int main() {
    CMyString empty;
    assert(empty.size() == 0);
    assert(std::strcmp(empty.c_str(), "") == 0);

    CMyString source("cat");
    assert(source.size() == 3);
    assert(source[0] == 'c');

    CMyString copy = source;
    copy[0] = 'b';
    assert(std::strcmp(copy.c_str(), "bat") == 0);
    assert(std::strcmp(source.c_str(), "cat") == 0);

    CMyString assigned("old");
    assigned = source;
    assert(assigned == source);
    assigned = assigned; // Самоприсваивание
    assert(std::strcmp(assigned.c_str(), "cat") == 0);
    assert(!(assigned != source));

    const CMyString joined = source + CMyString("fish");
    assert(std::strcmp(joined.c_str(), "catfish") == 0);
    assert(std::strcmp(source.c_str(), "cat") == 0);

    CMyString doubled("ab");
    doubled += doubled; // Самоалиасинг
    assert(std::strcmp(doubled.c_str(), "abab") == 0);
    assert(std::strcmp((!doubled).c_str(), "baba") == 0);
    assert(std::strcmp((source ^ 2).c_str(), "catcat") == 0);
    assert(std::strcmp((source ^ 0).c_str(), "") == 0);

    const CMyString letters("abcdef");
    const CMyString selected = letters({5, 0, 2, 4});
    assert(std::strcmp(selected.c_str(), "face") == 0);

    bool bad_index = false;
    try {
        (void)letters[100];
    } catch (const std::out_of_range&) {
        bad_index = true;
    }
    assert(bad_index);

    std::ostringstream output;
    output << joined;
    assert(output.str() == "catfish");

    // Контракт ввода: читать одно слово, как std::string через operator>>.
    CMyString read("old");
    std::istringstream input("hello world");
    input >> read;
    assert(!input.fail());
    assert(std::strcmp(read.c_str(), "hello") == 0);

    std::cout << "CMyString: основные проверки пройдены.\n";
}
