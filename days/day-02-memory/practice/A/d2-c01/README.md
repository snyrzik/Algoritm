# d2-c01 · A1 · C-string Lab

Реализуйте char* concat_copy(const char*,const char*) через strlen, strcpy, strcat; возвращаемый new[]-буфер принадлежит вызывающему. nullptr → invalid_argument. Реализуйте int compare_text(const char*,const char*) через strcmp (контракт знака), void copy_ints(int* dst,const int* src,size_t n) через memcpy (диапазоны не пересекаются), void shift_left(char* text,size_t count) через memmove. count<=strlen, иначе out_of_range; nullptr разрешён только в copy_ints при n=0. Проверяйте переполнение размеров до выделения/умножения.

## Проверки

- Копирование и конкатенация
- Сравнение содержимого
- Массив int
- Перекрытие и пустая строка
- Некорректные аргументы
