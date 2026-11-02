# d3-c01 · A1 · checked_access

Напишите int checked_access(const int* array,std::size_t size,std::size_t index). Сначала проверяется nullptr → invalid_argument; затем index>=size → out_of_range. Верните значение элемента.

## Проверки

- Обычные индексы
- Пустой и неверный индекс
- nullptr имеет приоритет
- Очень большой индекс
