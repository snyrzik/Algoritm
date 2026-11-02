TASKS = []
TITLES = ['Перегрузка операторов', 'Память и CMyString', 'Шаблоны функций', 'Шаблоны классов и RTTI', 'Итоговый экзамен']
TOPICS = [['Классы', 'const correctness', 'References', 'Перегрузка операторов', 'Потоки'], ['Dynamic memory', 'Copy constructor', 'Assignment operator', 'Exception safety', 'C-строки'], ['Template deduction', 'Specialization', 'References', 'Exception safety'], ['Шаблоны классов', 'Наследование', 'Dynamic memory', 'RTTI'], ['Синтаксис', 'Проектирование', 'Dynamic memory', 'Exception safety', 'Specialization']]

def make_hints(task):
    title=task['title'].lower()
    if any(word in title for word in ('replace','присваив','транзакц','resource','tsequence','исключени')):
        return ['Найдите первую операцию, которая может бросить. Что уже изменено к этому моменту?', 'Сильная гарантия требует сохранения старого состояния при неудаче. Копирование T и выделение памяти могут бросать; освобождение старого ресурса должно происходить после успешной подготовки.', 'Разделите работу на проверку аргументов, подготовку отдельного нового состояния и финальную фиксацию. При подготовке учитывайте, что аргумент может указывать внутрь текущего объекта. Временный ресурс должен освобождаться при любом пути выхода.']
    if any(word in title for word in ('индекс','границ','доступ','checked','erase','сдвиг')):
        return ['Отдельно выпишите допустимый диапазон для каждой операции и проверьте его крайние точки.', 'Индекс элемента требует index < size. Пустой диапазон может допускать position == size. Не вычитайте position из size до проверки position: size_t беззнаковый.', 'Проверяйте position > size, затем count > size - position. В доступе к элементу нужны две перегрузки по const; изменение через [] требует ссылки, а при сдвиге C-строки переносится также завершающий ноль.']
    if any(word in title for word in ('rtti','cast','преобразов','динамическ','typeid')):
        return ['Сравните статический тип выражения и динамический тип объекта. Как контракт сообщает неудачу?', 'Проверяемое понижающее dynamic_cast требует полиморфную базу. Неудачный cast указателя даёт nullptr, ссылки — bad_cast. static_cast не проверяет динамический тип.', 'Сначала проверьте иерархию и виртуальный деструктор. Для точного динамического типа сравнивайте typeid-объекты через ==, а не реализационно-зависимое name(). Не разыменовывайте результат преобразования до проверки.']
    if any(word in title for word in ('поток','вывод','ввод')):
        return ['Проверьте направление операндов, возвращаемый поток и момент изменения объекта.', 'Свободный operator<< принимает ostream& слева и const-ссылку на объект справа. Возврат того же потока по ссылке обеспечивает цепочку. failbit и исключение потока — разные механизмы.', 'Сначала прочитайте и проверьте все значения и разделители во временное состояние. Только после полного успеха измените объект. Не выводите через cout внутри оператора, если ему передан другой поток.']
    if task['day']==2 or any(word in title for word in ('памят','буфер','копир','освобож','строк')):
        return ['Нарисуйте, какой объект владеет каждым буфером и когда этот буфер уничтожается.', 'C-строка требует size + 1 байт и завершающий ноль. new[] соответствует delete[], malloc — free. Копия владельца должна иметь независимый ресурс.', 'Проверьте пустой объект, nullptr, самоприсваивание и аргумент, ссылающийся внутрь текущего буфера. Для перекрывающегося переноса подходит memmove; длина переноса должна учитывать ноль. Не уничтожайте источник до завершения чтения.']
    if task['day'] in (3,4) or any(word in title for word in ('шаблон','специализац','внешн','template')):
        return ['Разделите параметры шаблона, аргументы функции и тип результата. Где каждый параметр объявлен?', 'При определении метода за классом нужны список template-параметров и квалификатор Class<T,...>::. Значение по умолчанию не повторяется. Полная специализация начинается с template<>.', 'Подставьте в свою сигнатуру сначала int, затем double или пользовательский тип. Проверьте const и ссылки отдельно. При конфликте вывода однотипного T явный аргумент шаблона отличается от добавления второго независимого параметра типа.']
    return ['Проверьте, должен ли результат быть новым значением или ссылкой на существующий объект.', 'const после метода относится к this. Возвращаемая ссылка должна обозначать объект, чьё время жизни продолжается после выхода. Составная операция обычно возвращает изменяемую ссылку на левый операнд.', 'Разберите одну цепочку вызовов по шагам: какой объект меняется на каждом шаге, какой тип имеет результат и можно ли вызвать метод для const-объекта. Для неизменяющей арифметики сравните операнды до и после операции.']

def add(day, kind, title, prompt, **extra):
    index = 1 + sum(t['day'] == day and t['kind'] == kind for t in TASKS)
    task = dict(id=f'd{day}-{kind.lower()}{index:02}', day=day, kind=kind, title=title, prompt=prompt, level='A', minutes={'Q': 2, 'S': 4, 'P': 4, 'D': 10, 'C': 30}[kind], tags=[TOPICS[day-1][0]], required=True, **{k:v for k,v in extra.items() if k not in ('level','minutes','tags','required')})
    task.update({k:v for k,v in extra.items() if k in ('level','minutes','tags','required')})
    task['order'] = len(TASKS)
    task.setdefault('hints', make_hints(task))
    TASKS.append(task)
    return task

def quiz(day, title, prompt, options, answer, explanation, tags=None, kind='Q', category=None):
    return add(day, kind, title, prompt, options=options, answer=answer if isinstance(answer,list) else [answer], explanation=explanation, optionExplanations=[f'{v} — '+explanation for v in options], multiple=isinstance(answer,list), tags=tags or [TOPICS[day-1][0]], **({'category':category} if category else {}))

def code(day, kind, title, prompt, cases, *, starter='// Напишите решение с нуля. Добавьте необходимые заголовки.\n', prefix='', suffix='', checks='', level='A', memory=False, tags=None, minutes=None, **extra):
    tests = [dict(name=n, code=c, category=cat) for n,c,cat in cases]
    return add(day, kind, title, prompt, starter=starter, prefix=prefix, suffix=suffix, checks=checks, tests=tests, level=level, memory=memory, tags=tags or [TOPICS[day-1][0]], minutes=minutes or (4 if kind=='S' else 12 if kind=='D' else 35), **extra)

def case(name, body, category='functional'): return (name,body,category)

PREAMBLE = '''#include <cstddef>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <sstream>
#include <string>
#include <stdexcept>
#include <type_traits>
#include <limits>
#include <utility>
#include <typeinfo>
#include <complex>
#include "support.hpp"
'''
