// Лекция 4, проект 2. Скомпилировать со своим bidirectional_list.hpp.
#include "bidirectional_list.hpp"

#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>

int main() {
    BidirectionalList<int> values;
    assert(values.empty());
    assert(values.size() == 0U);

    values.push_back(2);
    values.push_front(1);
    values.push_back(4);            // 1, 2, 4
    values.insert_before(2, 3);     // 1, 2, 3, 4
    assert(values.size() == 4U);
    assert(values.front() == 1);
    assert(values.back() == 4);
    assert(values.at(0) == 1);
    assert(values.at(2) == 3);
    assert(values.at_from_back(0) == 4);
    assert(values.at_from_back(3) == 1);

    const BidirectionalList<int>& readonly = values;
    assert(readonly.at(1) == 2);
    assert(readonly.at_from_back(1) == 3);

    values.at(1) = 20;              // 1, 20, 3, 4
    assert(values.at(1) == 20);
    values.erase_at(0);             // 20, 3, 4
    values.erase_at(2);             // 20, 3
    values.insert_before(values.size(), 5); // 20, 3, 5
    assert(values.at_from_back(0) == 5);
    assert(values.at_from_back(1) == 3);
    assert(values.at_from_back(2) == 20);
    assert(values.pop_back() == 5);
    assert(values.pop_front() == 20);
    assert(values.pop_front() == 3);
    assert(values.empty());

    bool failed = false;
    try {
        values.erase_at(0);
    } catch (const std::out_of_range&) {
        failed = true;
    }
    assert(failed);

    failed = false;
    try {
        (void)values.pop_back();
    } catch (const std::out_of_range&) {
        failed = true;
    }
    assert(failed);

    BidirectionalList<std::string> names;
    names.push_back("A");
    names.push_back("B");
    names.push_back("C");
    BidirectionalList<std::string> copy(names);
    names.erase_at(1);
    assert(copy.size() == 3U);
    assert(copy.at(1) == "B");
    assert(copy.at_from_back(0) == "C");

    BidirectionalList<std::string> assigned;
    assigned = copy;
    assigned = assigned;
    assert(assigned.size() == 3U);
    assert(assigned.pop_back() == "C");
    assert(assigned.pop_back() == "B");
    assert(assigned.pop_back() == "A");
    assert(assigned.empty());

    std::cout << "BidirectionalList: basic checks passed\n";
}
