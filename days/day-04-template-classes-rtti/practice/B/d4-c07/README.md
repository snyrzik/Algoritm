# d4-c07 · B4 · RTTI Laboratory

Создайте абстрактную Shape с virtual double area() const и виртуальным деструктором. Rectangle(double width,double height), Circle(double radius) наследуют Shape, отрицательные размеры → invalid_argument, ноль допустим. Площадь окружности использует pi=3.141592653589793. Напишите Rectangle* as_rectangle(Shape*), Rectangle& require_rectangle(Shape&), bool is_exact_circle(const Shape&) (typeid), Shape* upcast(Rectangle*) (static_cast). Для неудачного cast указателя → nullptr, ссылки → bad_cast. Не сравнивайте строки type_info::name().

## Проверки

- Виртуальные площади
- Успешные преобразования
- Неудачные преобразования
- Точный динамический тип
- Нулевые и отрицательные размеры
