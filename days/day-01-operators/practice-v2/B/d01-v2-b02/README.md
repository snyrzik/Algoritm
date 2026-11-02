# B2 · Композиция фильтров

### B2. Композиция фильтров и переиспользование кода

Написать **свободные функции вне классов**:

- `AudioBlock apply_filter(const AudioBlock& input, const ChannelMix& mix)` — возвращает отфильтрованный блок.
- `AudioBlock apply_chain(const AudioBlock& input, const ChannelMix& first, const ChannelMix& second)` — применяет `first`, затем `second`; можно использовать существующий интерфейс, не дублируя вычисление коэффициентов вручную.
- `bool approximately_same(const AudioBlock& a, const AudioBlock& b, double epsilon)` — сравнивает размеры и значения компонентов всех отсчётов; для отрицательного `epsilon` выбрасывает `std::invalid_argument`.

**Обязательные идеи:** `const`-ссылки, возвращение по значению, переиспользование `operator()`, композиция преобразований, сравнение вещественных величин, отсутствие случайных изменений входных объектов.

**Тесты:**

- Для произвольного блока `apply_chain(input, A, B)` должен быть эквивалентен `apply_filter(input, B*A)` в пределах допуска; **не** `A*B`.
- Проверить два некоммутирующих микшера.
- Пустой блок.
- Полный блок.
- Несовпадающие размеры.
- `epsilon == 0` и отрицательный `epsilon`.
- Исходный `input` не меняется.

Подключите заголовки StereoSample.hpp, ChannelMix.hpp и AudioBlock.hpp. Используются ваши A1–A3, без подмены чужими реализациями.
