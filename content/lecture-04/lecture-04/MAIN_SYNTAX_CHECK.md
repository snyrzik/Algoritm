# Как пользоваться локальными проверочными `main.cpp`

Рядом с твоими заголовочными файлами размести соответствующий `MAIN_*.cpp`:

- `MAIN_FORWARD_CHAIN.cpp` → `forward_chain.hpp` (шаблон `ForwardChain<T>`).
- `MAIN_BIDIRECTIONAL_LIST.cpp` → `bidirectional_list.hpp` (шаблон `BidirectionalList<T>`).
- `MAIN_COLLECTION_LAB.cpp` → `collection_operations.hpp` (функции внутри `namespace collection_lab`).

Запуск на компьютере пользователя:

```bash
g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic -Werror MAIN_FORWARD_CHAIN.cpp -o check_forward
./check_forward

g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic -Werror MAIN_BIDIRECTIONAL_LIST.cpp -o check_double
./check_double

g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic -Werror MAIN_COLLECTION_LAB.cpp -o check_stl
./check_stl
```

На Windows запуск `.exe` выполняется через `check_forward.exe` (или `./check_forward.exe` в поддерживаемом терминале).

Так как первые два проекта являются шаблонами классов, их определения рекомендуется помещать в соответствующие заголовочные файлы, чтобы они были доступны в точке инстанцирования.

**Важно:** не компилировать с `-DNDEBUG`, поскольку он отключает стандартные `assert`.

При поддержке GCC или Clang можно добавить `-g -fsanitize=address,undefined -fno-omit-frame-pointer` для диагностики ошибок памяти. При этом сам `main` не доказывает отсутствие всех ошибок: необходимы дополнительные тесты в собственной IDE и внимательное ревью.
