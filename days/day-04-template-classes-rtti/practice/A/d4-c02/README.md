# d4-c02 · A2 · FixedBuffer<T, Size>

Создайте template<class T,int Size=256> class FixedBuffer. Size должен быть положительным (static_assert). Храните собственный массив, элементы value-initialized. capacity() const -> std::size_t возвращает Size. Две версии [] возвращают T& / const T&, индекс>=Size → out_of_range. Не используйте STL-контейнеры.

## Проверки

- Вместимость и начальные значения
- Ссылки и const
- Границы
- Пользовательский тип
