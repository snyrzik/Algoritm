cmake_minimum_required(VERSION 3.20)
project(CppMastery LANGUAGES NONE)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
enable_testing()
add_test(NAME infrastructure COMMAND ${Python3_EXECUTABLE} -m unittest discover -s tests -v)
set_tests_properties(infrastructure PROPERTIES WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} ENVIRONMENT "PYTHONUTF8=1")
foreach(DAY RANGE 1 5)
  add_custom_target(day-${DAY}
    COMMAND ${Python3_EXECUTABLE} tools/check.py --day ${DAY}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking independent C++ exercises for day ${DAY}")
endforeach()
