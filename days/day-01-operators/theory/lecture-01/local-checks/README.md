# Локальная проверка первой лекции

Эти три `main.cpp` написаны для того, чтобы **тестировать твои реализации на твоём компьютере**. Здесь нет готовых классов, сайтовой компиляции или сложного тестового фреймворка.

## Что делать

1. Выбери проект (`Matrix2x2`, `CMyString`, `DynamicVector`).
2. Напиши требуемые `.hpp` и `.cpp` (или один заголовочный файл с реализацией).
3. Скопируй соответствующий `main.cpp` рядом с заголовками.
4. Собери своим локальным компилятором.
5. Если все `assert` прошли, программа напечатает сообщение об успешной базовой проверке.
6. Проверка `assert` не заменяет проверки ошибок памяти и крайних случаев.

### Пример GCC / MinGW

```bash
g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic main.cpp Matrix2x2.cpp -o check_matrix
./check_matrix
```

Если реализации находятся только в заголовочном файле, `.cpp` после `main.cpp` добавлять не нужно.

Для строк:

```bash
g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic main.cpp CMyString.cpp -o check_string
./check_string
```

Для динамического вектора:

```bash
g++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic main.cpp DynamicVector.cpp -o check_vector
./check_vector
```

На Windows с MinGW запускать `check_matrix.exe`, `check_string.exe`, `check_vector.exe`. Для Visual Studio можно создать Console App и добавить файлы проекта в решение.

### Проверка памяти через GCC/Clang (при поддержке среды)

Добавь к команде сборки:

```bash
-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer
```

`assert` должен быть включён. **Не компилируй с `-DNDEBUG`**, иначе стандартные проверки `assert` отключатся.

## Согласованный API

- `Matrix2x2.hpp`: класс `Matrix2x2` с конструктором `(double a,double b,double c,double d)`, конструктором по умолчанию, операторами `()`, `+`, `-`, унарным `-`, `*` (матрица, скаляр), `+=`, `==`, `!=`, `<<`, `>>` в формате `[[a,b],[c,d]]`.
- `Point2D.hpp`: структура `Point2D` с полями `double x`, `double y`, а также внешняя функция `Point2D transform(const Matrix2x2&, const Point2D&)`.
- `CMyString.hpp`: класс `CMyString` с конструктором по умолчанию, конструктором из `const char*`, копированием, присваиванием, деструктором, `size()`, `c_str()`, `[]`, `==`, `!=`, `+`, `+=`, унарным `!`, `operator^(std::size_t)` и `operator()(std::initializer_list<std::size_t>)`, `<<`, `>>` (читает одно слово).
- `DynamicVector.hpp`: класс `DynamicVector` с конструктором `(std::size_t size, double fill=0)`, копированием и присваиванием, `size()`, `[]`, `+`, `-`, `+=`, `*` для скалярного произведения двух векторов, `*` и `/` для скаляра, `==`, `!=`, `<<`, плюс внешняя функция `double triangle_area(const DynamicVector&, const DynamicVector&)` для двух двумерных векторов.

Это лишь **базовые проверки**. Если они прошли, следует ещё проверить исключения, динамическую память и поведение на более сложных входных данных. Сайт не должен объявлять полную готовность только на основании этих трёх `main`.
