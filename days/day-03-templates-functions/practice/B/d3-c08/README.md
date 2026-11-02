# d3-c08 · B3 · Generic Algorithms

Напишите три шаблона над обычными массивами: find_first(const T*,size_t,Predicate) -> size_t (индекс первого совпадения, при отсутствии — size); count_if(const T*,size_t,Predicate) -> size_t; swap_at(T*,size_t,size_t i,size_t j) -> void. Для первых двух nullptr допустим лишь при size=0. swap_at: nullptr → invalid_argument, любой индекс>=size → out_of_range, проверка предшествует изменению. Самоперестановка разрешена. Не используйте готовые алгоритмы STL. Сигнатуры оформите самостоятельно в соответствии с этими типами результатов.

## Проверки

- Поиск и подсчёт
- Пустые диапазоны
- Перестановка
- Ошибки сохраняют данные
- std::string
