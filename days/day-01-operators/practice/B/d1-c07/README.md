# d1-c07 · B4 · Состояние потоков

Напишите struct StreamReport { int first; double second; bool failed; bool ended; }; и StreamReport inspect_stream(const char* text). Создайте istringstream, последовательно прочитайте int, double, int. Первые два начальных значения 0. После третьей попытки сохраните fail() и eof(). nullptr → invalid_argument. В notes.md объясните разницу между этими битами и исключением.

## Проверки

- Некорректный третий токен
- Полный ввод
- Пробел в конце
- Неполный ввод
- Пустой ввод и nullptr
