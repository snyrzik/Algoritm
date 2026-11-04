"""Materialize lecture 1 from the supplied author text; never overwrite learner files."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT
from tools.content.lecture01_checks import SCORE, SCORE_TYPES, DURATION, DURATION_TYPES, HISTORY, HISTORY_TYPES, CLOCK, CLOCK_TYPES

DAY = ROOT / 'days/day-01-operators'
LECTURE = DAY / 'theory/lecture-01'

TEXT_HOLDER = '''// Исходный класс с дефектом копирования. Исправьте самостоятельно.
#include <cstddef>
#include <cstring>
#include <stdexcept>
class TextHolder {
    char* data_;
public:
    explicit TextHolder(const char* text) {
        data_ = new char[std::strlen(text) + 1];
        std::strcpy(data_, text);
    }
    ~TextHolder() { delete[] data_; }
    const char* c_str() const { return data_; }
    char& operator[](std::size_t index) {
        if (index >= std::strlen(data_)) throw std::out_of_range("index");
        return data_[index];
    }
};
'''
HOLDER_CASES = [
    dict(name='Копия владеет независимым буфером', category='ownership', code='TextHolder a("cat"); TextHolder b(a); b[0]=\'b\'; CHECK(std::strcmp(a.c_str(),"cat")==0); CHECK(std::strcmp(b.c_str(),"bat")==0); CHECK(a.c_str()!=b.c_str());'),
    dict(name='Присваивание и самоприсваивание', category='ownership', code='TextHolder a("cat"), b("long old value"); b=a; b[0]=\'r\'; CHECK(std::strcmp(a.c_str(),"cat")==0); b=mastery_alias(b); CHECK(std::strcmp(b.c_str(),"rat")==0);'),
    dict(name='Копия живёт после уничтожения оригинала', category='lifetime', code='TextHolder* copy=nullptr; {TextHolder original("alive"); copy=new TextHolder(original);} CHECK(std::strcmp(copy->c_str(),"alive")==0); delete copy;'),
    dict(name='Пустая строка и место для нулевого символа', category='boundary', code='const TextHolder empty(""); CHECK(empty.c_str()!=nullptr && empty.c_str()[0]==0); const TextHolder one("x"); CHECK(one.c_str()[1]==0);'),
]

PROJECTS = [
    ('Matrix2x2', 'Matrix2x2 + Point2D', '''Самостоятельно создайте матрицу 2×2 и точку. Реализацию классов сайт не предоставляет.

1. **Объект и доступ.** Конструкторы по умолчанию и `(double a, double b, double c, double d)`; изменяемый и константный `operator()(row, col)`. Индексы вне 0…1 приводят к `std::out_of_range`.
2. **Арифметика.** `+`, `-`, унарный `-`, матричное умножение, `+=`, умножение на `double` с обеих сторон, `==`, `!=`. Матричное умножение зависит от порядка. Неизменяющие операции сохраняют исходные объекты; `+=` возвращает ссылку на левый.
3. **Потоки.** Точный формат `[[a,b],[c,d]]`. Ошибка ввода устанавливает `failbit` и сохраняет прежнюю матрицу. Операторы возвращают исходный поток для цепочек.
4. **Точка.** В `Point2D.hpp` объявите структуру с полями `double x`, `double y` и внешнюю функцию `Point2D transform(const Matrix2x2&, const Point2D&)`.

Дополнительный договор для самостоятельной проверки: матрица по умолчанию нулевая; для вещественного сравнения используйте и документируйте абсолютный допуск `1e-9`.
''', ['Нулевая и единичная матрица; доступ к четырём элементам', 'A * B и B * A: порядок умножения', 'Скаляр слева и справа; const-операнды; цепочка +=', 'Индексы 2 и отрицательный индекс после преобразования к size_t', 'Правильный формат, неверный разделитель, неполный ввод и сохранение объекта', 'Преобразование точки; нулевая матрица и начало координат']),
    ('CMyString', 'CMyString', '''Самостоятельно создайте класс, владеющий собственным `char[]`. Не подменяйте владение готовым строковым контейнером.

1. **Инвариант и ресурс.** Конструктор по умолчанию, конструктор из `const char*`, `size()`, `c_str()`. Буфер содержит завершающий `\\0`; пустая строка корректна.
2. **Правило трёх.** Глубокое копирование, присваивание и деструктор. Копии независимы; самоприсваивание безопасно.
3. **Операторы.** Изменяемая и константная индексация, сравнение содержимого, `+`, `+=`, переворот через `!`, повторение через `operator^(std::size_t)`, выборка через `operator()(std::initializer_list<std::size_t>)`. `s += s` работает корректно. Недопустимый индекс вызывает `std::out_of_range`.
4. **Потоки.** `<<` печатает содержимое; `>>` читает одно слово. При ошибке ввода сохраняется прежнее значение. Возвращайте исходный поток.

Проверьте освобождение каждого выделенного буфера и независимость времени жизни копий. Перед выделением памяти для повторения учитывайте переполнение размера; политику для `nullptr` явно опишите в своём решении.
''', ['Пустая строка, один символ, завершающий ноль', 'Глубокая копия, присваивание, самоприсваивание и жизнь после оригинала', 's += s; сложение не меняет исходные строки', '!s; повторение 0, 1 и несколько раз', 'Выборка индексов в другом порядке; повторяющиеся и недопустимые индексы', 'Чтение одного слова; пустой/ошибочный поток и состояние объекта', 'Баланс new[]/delete[] и анализ ошибок памяти в своей среде']),
    ('DynamicVector', 'DynamicVector', '''Создайте **не шаблонный** вектор `double` произвольной размерности с собственным динамическим массивом. Шаблон `DynamicVector<T>` на этом этапе не требуется.

1. **Ресурс и доступ.** Конструктор `(std::size_t size, double fill=0)`, `size()`, глубокое копирование, присваивание, деструктор, изменяемый и константный `[]`.
2. **Арифметика.** `+`, `-`, `+=`, скалярное произведение двух векторов через `*`, умножение на скаляр с обеих сторон и деление на скаляр. `+=` поддерживает цепочки, неизменяющие операции сохраняют операнды.
3. **Сравнение и ошибки.** `==`, `!=` с документированным абсолютным допуском `1e-9`. Несовпадающие размерности в арифметике приводят к `std::invalid_argument`, неверный индекс — к `std::out_of_range`. Векторы разных размерностей не равны. Деление на ноль отклоняется с `std::invalid_argument`.
4. **Вывод и геометрия.** `<<` выводит все координаты (формат опишите сами). Внешняя `double triangle_area(const DynamicVector&, const DynamicVector&)` для двух двумерных векторов возвращает площадь треугольника с общим началом; для других размерностей — `std::invalid_argument`.

Размерность 0 допустима: нет элементов, неверен любой индекс. Самоприсваивание безопасно, копии не разделяют ресурс.
''', ['Размерности 0, 1, 2 и больше; заполнение', 'Независимость копий, присваивание, самоприсваивание', 'Оба const/изменяемый доступа; индекс size()', 'Разные размерности для +, -, += и скалярного произведения', 'Умножение с двух сторон, ноль и деление на ноль', 'Сравнение в пределах допуска и вне него', 'Площадь: обычный, коллинеарный и нулевой векторы; неверная размерность']),
]

def write_task(task, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'exercise.json').write_text(json.dumps(task, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    (folder/'README.md').write_text((task['prompt']+'\n\n'+task.get('protocol','')).rstrip()+'\n', encoding='utf-8', newline='\n')

def main():
    raw=(LECTURE/'theory.md').read_bytes()
    markdown=raw.decode('utf-8')
    chapters=re.split(r'(?m)^# Глава \d\.', markdown)[1:]
    if len(chapters)!=5: raise ValueError('Expected five authored chapters')
    cases=[SCORE,DURATION,HISTORY,HOLDER_CASES,CLOCK]
    types=[SCORE_TYPES,DURATION_TYPES,HISTORY_TYPES,'',CLOCK_TYPES]
    names=['ScoreCounter','Duration','FixedHistory','TextHolder','ClockTime']
    adapters=[('score_read = &ScoreCounter::points', 'score_add = &ScoreCounter::add'), ('duration_read = &Duration::seconds',), (), (), ()]
    for chapter in range(1,6):
        found=re.search(r'(?ms)^## (?:Закрепление после главы|Самостоятельное закрепление главы).*?(?=^---|^# |\Z)', chapters[chapter-1])
        if not found: raise ValueError(f'Missing check {chapter}')
        task_id=f'l01-v3-c{chapter:02}'
        task=dict(id=task_id, day=1, kind='D' if chapter==4 else 'C', level='A', required=True, version=3, section='lecture-theory', lecture=1, chapter=chapter, title=f'Закрепление {chapter} · {names[chapter-1]}', order=10000+chapter, minutes=25, prompt=found[0].rstrip(), tags=['Лекция № 1',names[chapter-1]], starter=TEXT_HOLDER if chapter==4 else '// Самостоятельное решение. Добавьте нужные заголовки и напишите класс.\n', prefix='', suffix='', checks=types[chapter-1], tests=cases[chapter-1], memory=False, filePath=f'student/day-01/{task_id}/solution.hpp', hints=[])
        if adapters[chapter-1]:
            adapter='#pragma once\n// Укажите имена своих методов; реализация остаётся вашей.\nnamespace mastery_check {\n'+''.join('inline constexpr auto '+line+';\n' for line in adapters[chapter-1])+'}\n'
            task['starterFiles']={'test_adapter.hpp':adapter}
            task['suffix']='\n#include "test_adapter.hpp"\n'
            task['protocol']='Имена методов чтения и изменения выберите самостоятельно. В test_adapter.hpp укажите указатели на них; points/add/seconds — исходные настройки, не обязательные имена API.'
        if chapter==4:
            task['protocol']='В пакете не задан точный API TextHolder. Для готового main используется открытый учебный протокол: конструктор из const char*, c_str() const и изменяемый operator[]. Ниже дан исходный класс с дефектом, а не готовое решение. В notes.md объясните владельцев, время жизни, самоприсваивание и место для нулевого символа; отдельно проверьте память в своей IDE.'
        if chapter==5:
            task['protocol']='HH:MM — ровно две цифры, двоеточие, две цифры. Ведущие пробелы разрешены. Некорректный конструктор: std::invalid_argument или std::out_of_range. В notes.md объясните сохранение fill, flags и precision потока.'
        write_task(task, LECTURE/'checks'/task_id)
    for number,(name,title,prompt,edges) in enumerate(PROJECTS,1):
        task_id=f'l01-v3-p{number:02}'
        headers=[name+'.hpp']+(['Point2D.hpp'] if number==1 else [])
        task=dict(id=task_id, day=1, kind='C', level='A', required=True, version=3, section='lecture-practice', lecture=1, title=title, project=name, order=number, minutes=[90,150,150][number-1], prompt=prompt, tags=['Лекция № 1', 'Самостоятельный проект'], filePath=f'student/day-01/{task_id}/{headers[0]}', starterFiles={**{h:'// Напишите класс самостоятельно. Добавьте нужные заголовки.\n' for h in headers}, name+'.cpp':'// Определения методов, если реализация не целиком в заголовке.\n'}, localMain=f'local-checks/{name}/main.cpp', publicChecks=edges, expectedOutput=f'{name}: основные проверки пройдены.\n', hints=[])
        write_task(task, DAY/'practice'/task_id)
    manifest=dict(day=1, lecture=1, sourceFilename='Lecture_01_FULL_THEORY.md', sourceSha256=hashlib.sha256(raw).hexdigest(), checkIds=[f'l01-v3-c{i:02}' for i in range(1,6)], projectIds=[f'l01-v3-p{i:02}' for i in range(1,4)])
    (LECTURE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (DAY/'README.md').write_text('# Лекция № 1. Перегрузка операций\n\nПять авторских глав, пять самостоятельных закреплений, три проекта: Matrix2x2 + Point2D, CMyString, DynamicVector.\n\nОткрыть: http://127.0.0.1:8765/#/day/1\n\nПроверки запускаются в собственной IDE. Сайт сохраняет только ручную отметку «Отмечено мной»; базовый main не подтверждает полную корректность и безопасность памяти.\n',encoding='utf-8',newline='\n')
    print('Lecture 1 ready: five chapters, five checks, three local projects. Learner files were not overwritten.')

if __name__=='__main__':main()
