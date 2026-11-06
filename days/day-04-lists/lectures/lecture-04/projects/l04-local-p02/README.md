## Проект 2. `BidirectionalList<T>` — двусвязный список

**Цель:** научиться поддерживать взаимные ссылки, оба конца и размер списка при любой последовательности операций.

### Обязательный интерфейс

```cpp
#include <cstddef>

template <typename T>
class BidirectionalList {
public:
    BidirectionalList();
    BidirectionalList(const BidirectionalList& other);
    BidirectionalList& operator=(const BidirectionalList& other);
    ~BidirectionalList();

    bool empty() const;
    std::size_t size() const;
    const T& front() const;
    const T& back() const;
    T& at(std::size_t index);
    const T& at(std::size_t index) const;
    const T& at_from_back(std::size_t offset) const;

    void push_front(const T& value);
    void push_back(const T& value);
    T pop_front();
    T pop_back();
    void insert_before(std::size_t index, const T& value);
    void erase_at(std::size_t index);
    void clear();
};
```

### Семантика

- В пустом списке и `head`, и `tail` равны `nullptr`.
- `front`/`back`, `pop_front`/`pop_back` для пустого списка бросают `std::out_of_range`.
- `at(index)` допустим для `0 <= index < size()`; иначе `std::out_of_range`.
- `at_from_back(0)` — последний элемент; `at_from_back(size()-1)` — первый.
- `push_front`, `push_back`, `pop_front`, `pop_back` должны быть `O(1)` по числу изменяемых связей (без учёта стоимости создания/копирования `T`).
- `insert_before(index, value)` допустим для `0 <= index <= size()`. При `index == size()` добавить в конец. В противном случае вставить перед элементом с индексом `index`.
- `erase_at(index)` удаляет элемент с индексом `index`; индекс за диапазоном вызывает исключение.
- `at` и `insert_before` по индексу обычно требуют `O(N)` из-за поиска позиции, даже если изменение связей `O(1)`.
- Копирование глубокое, порядок сохраняется; самоприсваивание корректно.
- После каждого изменения соблюдены взаимные связи `next`/`prev`, состояние `head/tail`, корректный размер.

### Этапы

1. Пустой список и одноэлементное состояние.
2. Вставка в оба конца и удаление с обоих концов.
3. Чтение по прямому и обратному индексам.
4. Вставка перед произвольной позицией, включая обе границы.
5. Удаление начала, середины и конца.
6. Копирование, присваивание и очистка.
7. Анализ ошибок указателей, собственные тесты, объяснение сложности.

### Обязательные проверки

Проверить последовательность из разных вставок и удалений, а не отдельные изолированные вызовы; после каждого изменения сверить `front`, `back`, `at`, `at_from_back`, `size`, `empty`. Отдельно — пустой, единственный узел, копия, самоприсваивание и `std::string`.

### Вопросы для защиты

Почему одного обновления `next` недостаточно? Зачем `tail`? В чём различие между «вставить при известном адресе узла» и «вставить по индексу»? Почему после удаления головы нужно исправить `prev` у новой головы?

---

### Самостоятельная реализация

Первые два проекта — собственные узлы без STL-контейнеров. CollectionLab специально учит применять vector, list и deque; запрет из ЛР № 1 на него не переносится.
