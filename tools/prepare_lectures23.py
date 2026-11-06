"""Add the supplied lectures without modifying existing exercises or learner files."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,DAY_NAMES

SOURCE=ROOT/'content/lectures-02-03'

def block(markdown,start,end=None):
    text=markdown.split(start,1)[1]
    return start+(text.split(end,1)[0] if end else text)

DEFINITIONS={
 2:dict(title='Лекция № 2. Память, владение ресурсом и исключения (переходный модуль)',
        attribution='Восстановленный переходный модуль. Оригинальный университетский PDF лекции № 2 недоступен; этот текст не является исходными слайдами преподавателя.',
        checks=['Один буфер, три операции','Кому принадлежит массив?','Безопасный диапазон','Разбор ошибки без запуска'],
        projects=[
         dict(title='CMyString · безопасное редактирование',start='### Проект 1:',end='### Проект 2:',files=['CMyString.h','CMyString.hpp','CMyString.cpp'],base='l01-v3-p02',inherit=['CMyString.hpp','CMyString.cpp'],mains=['MAIN_CMYSTRING_EDITING.cpp'],steps=['Диапазоны и сохранение состояния при ошибке','erase в существующем буфере без аллокации','Подготовка новой строки и контроль переполнения','Самоалиасинг replacement','Исключения, инварианты и память']),
         dict(title='DynamicVector · изменение размера',start='### Проект 2:',end='### Как проверять освоение',files=['DynamicVector.h','DynamicVector.hpp','DynamicVector.cpp'],base='l01-v3-p03',inherit=['DynamicVector.hpp','DynamicVector.cpp'],mains=['MAIN_DYNAMICVECTOR_EDITING.cpp'],steps=['Инварианты размера, буфера и копий','resize: рост, уменьшение, неизменный размер','insert: начало, середина и конец','erase без нового выделения памяти','Пустое состояние, исключения и память'])]),
 3:dict(title='Лекция № 3. Шаблоны, приведение типов и RTTI',
        attribution='Материал по 25 слайдам презентации Е. В. Мясникова «Шаблоны. Приведение типов и RTTI», с пояснениями для C++17. Указание источника сохранено из предоставленного пакета.',
        checks=['Что компилятор должен вывести?','Синтаксис класса и состояния стека','Два стека — один интерфейс','RTTI · проверяемые преобразования'],
        projects=[
         dict(title='Шаблонные функции и строки',start='## Проект 1.',end='## Проект 2.',files=['GenericAlgorithms.h'],mains=['MAIN_GENERIC_FUNCTIONS.cpp'],steps=['Сигнатуры шаблонных функций и требования к T','Ссылки, самоприменение и пользовательский тип','Первое вхождение минимума и ошибочные входы','Перегрузка и полная специализация для C-строк']),
         dict(title='FixedStack<T, Capacity>',start='## Проект 2.',end='## Проект 3.',files=['FixedStack.h'],mains=['MAIN_FIXED_STACK.cpp'],steps=['Capacity > 0, массив и логический размер','LIFO и границы вместимости','Пустой pop/peek сохраняет out','Три определения методов вне тела класса','Исключения присваивания T']),
         dict(title='IStack<T> и LinkedStack<T>',start='## Проект 3.',end='## RTTI',files=['IStack.h','LinkedStack.h','FixedStack.h','PostfixEvaluator.h'],base='l03-local-p02',inherit=['FixedStack.h'],mains=['MAIN_LINKED_STACK.cpp','MAIN_POSTFIX.cpp'],steps=['Абстрактный интерфейс и виртуальный деструктор','Узлы без требования default-конструктора T','Глубокие копии, порядок и самоприсваивание','Исключения, владение узлами и полиморфизм','Доработка существующего FixedStack с override','Отдельный прикладной этап: постфиксный вычислитель'])])
}

DEFECTS={
 (2,2):'''// Частичный исходный класс с намеренным дефектом. Исправьте копирование.
#include <cstddef>
class IntBuffer {
    int* data_;
    std::size_t size_;
public:
    explicit IntBuffer(std::size_t size): data_(new int[size]{}), size_(size) {}
    ~IntBuffer() { delete[] data_; }
    IntBuffer(const IntBuffer&) = default; // Проверьте владение ресурсом.
    // Самостоятельно добавьте присваивание и необходимый доступ к элементам.
};
''',
 (2,4):'''// Фрагмент с дефектом из условия. Изучите без запуска с неверным диапазоном.
// Предполагаются поля m_data и m_size вашего CMyString.
void erase(std::size_t position, std::size_t count) {
    if (count > m_size) throw std::out_of_range("count");
    std::memmove(m_data + position, m_data + position + count,
                 m_size - position - count + 1);
    m_size = std::strlen(m_data);
}
'''
}

def make_main(number,name):
    text=(SOURCE/f'lecture-{number:02}'/name).read_bytes().decode('utf-8')
    output=re.search(r'std::cout\s*<<\s*"([^"\n]+)"',text)
    return dict(id=Path(name).stem.lower(),filename=name,sourcePath=f'lecture-{number:02}/{name}',expectedOutput=output[1].replace('\\n','\n') if output else '')

def write(task,folder):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'exercise.json').write_text(json.dumps(task,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (folder/'README.md').write_text(task['prompt'].rstrip()+'\n',encoding='utf-8',newline='\n')

def main():
    navigation=[]
    for number,definition in DEFINITIONS.items():
        source=SOURCE/f'lecture-{number:02}'
        raw=(source/f'LECTURE_{number:02}_THEORY.md').read_bytes();markdown=raw.decode('utf-8')
        instructions=(source/'CODEX_INSTRUCTIONS.md').read_bytes().decode('utf-8')
        folder=ROOT/'days'/f'day-{number:02}-{DAY_NAMES[number-1]}'/'lectures'/f'lecture-{number:02}'
        manifest=dict(number=number,title=definition['title'],attribution=definition['attribution'],sourceFilename=f'LECTURE_{number:02}_THEORY.md',sourceSha256=hashlib.sha256(raw).hexdigest(),checkIds=[],projectIds=[])
        chapter_matches=list(re.finditer(r'^# Глава [1-4]\..+$',markdown,re.M))
        if len(chapter_matches)!=4:raise ValueError('Expected four chapters')
        navigation.append(dict(number=number,title=definition['title'],attribution=definition['attribution'],chapters=[dict(id=f'chapter-{i+1}',title=m[0][2:].strip()) for i,m in enumerate(chapter_matches)]))
        for chapter,name in enumerate(definition['checks'],1):
            part=markdown[chapter_matches[chapter-1].start():chapter_matches[chapter].start() if chapter<4 else len(markdown)]
            check=re.search(r'^### Закрепление .+?(?=\r?\n---|\r?\n# |\Z)',part,re.M|re.S)
            if not check:raise ValueError(f'Missing check {number}/{chapter}')
            task_id=f'l{number:02}-local-c{chapter:02}'
            files=['RttiLab.h'] if (number,chapter)==(3,4) else ['solution.cpp']
            task=dict(id=task_id,day=number,lecture=number,chapter=chapter,packLecture=number,section='lecture-theory',kind='C',level='A',required=True,version=4,order=10000+chapter,title=f'Закрепление {chapter} · {name}',prompt=check[0].rstrip(),minutes=25,tags=[f'Лекция № {number}',name],localAssessment=True,starterFiles={name:DEFECTS.get((number,chapter),'// Самостоятельное закрепление. Код и объяснение напишите сами.\n') for name in files},filePath=f'student/day-{number:02}/{task_id}/{files[0]}',reviewRequirements=['Выполнены все пункты авторского условия','Проверены корректные и ошибочные случаи','Записано объяснение выбранного решения'],localMains=[])
            if (number,chapter)==(3,4):
                task['prompt']+='\n\n'+block(instructions,'## RTTI', '## Компиляция')
                task['localMains']=[make_main(3,'MAIN_RTTI.cpp')]
            write(task,folder/'checks'/task_id);manifest['checkIds'].append(task_id)
        for index,project in enumerate(definition['projects'],1):
            task_id=f'l{number:02}-local-p{index:02}'
            prompt=block(instructions,project['start'],project['end']).rstrip()
            prompt=prompt.replace('Создай условие для трёх заголовков ученика:', 'Самостоятельно создайте три заголовка:')
            prompt=prompt.replace('Предоставь только **условие и `MAIN_GENERIC_FUNCTIONS.cpp`**, но не готовый `GenericAlgorithms.h`.', 'Самостоятельно напишите `GenericAlgorithms.h`. Готовый `MAIN_GENERIC_FUNCTIONS.cpp` доступен для локальной проверки; реализации алгоритмов в нём нет.')
            prompt=prompt.replace('Ученик должен самостоятельно написать заголовочный файл', 'Самостоятельно напишите заголовочный файл')
            starter={name:'// Продолжите собственную реализацию. Готового решения здесь нет.\n' for name in project['files']}
            if number==2:
                stem='CMyString' if index==1 else 'DynamicVector'
                starter[stem+'.h']='#pragma once\n#include "'+stem+'.hpp"\n'
                prompt+='\n\n### Совместимость с вашей первой лекцией\n\nПроверочный файл пакета включает `.h`, а первая лекция использует `.hpp`. Файл `.h` в черновике — только переходный include вашего `.hpp`; он не содержит реализации класса. Если ваш код уже сохранён на сайте, его текущая версия один раз копируется в новый черновик. Исходные файлы и результаты первой лекции не изменяются. Можно продолжить тот же класс напрямую в своей IDE.'
            task=dict(id=task_id,day=number,lecture=number,packLecture=number,section='lecture-practice',kind='C',level='A',required=True,version=4,order=10100+index,title=project['title'],project=project['title'],prompt=prompt,minutes=120 if number==2 else 150,tags=[f'Лекция № {number}','Самостоятельный проект'],localAssessment=True,starterFiles=starter,filePath=f'student/day-{number:02}/{task_id}/{project["files"][0]}',localMains=[make_main(number,name) for name in project['mains']],projectSteps=project['steps'],reviewRequirements=['Базовый main запущен со своей реализацией','Дополнительные пограничные и ошибочные случаи разобраны','Требования к владению, исключениям и типам проверены'],hints=[])
            if project.get('base'):
                task['continuationOf']=project['base'];task['inheritFiles']={name:dict(task=project['base'],name=name) for name in project['inherit']}
            write(task,folder/'projects'/task_id);manifest['projectIds'].append(task_id)
        (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    nav_path=ROOT/'app/src/lectures/catalog.json'
    previous=json.loads(nav_path.read_text(encoding='utf-8')) if nav_path.exists() else []
    navigation+=[item for item in previous if item['number'] not in DEFINITIONS]
    nav_path.write_text(json.dumps(sorted(navigation,key=lambda item:item['number']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    course_path=ROOT/'days/course.json'
    previous=json.loads(course_path.read_text(encoding='utf-8'));first=previous[0]
    course=[first,
            dict(id=2,title='Память, владение ресурсом и исключения',subtitle='Восстановленный переходный модуль',topics=['C-строки','RAII','Исключения','Редактирование данных'],duration='В своём темпе'),
            dict(id=3,title='Шаблоны, приведение типов и RTTI',subtitle='От шаблонных функций к копируемому стеку',topics=['Шаблоны функций','Шаблоны классов','Наследование','RTTI'],duration='В своём темпе')]
    course+=[item for item in previous if item['id'] not in (1,2,3)]
    course_path.write_text(json.dumps(sorted(course,key=lambda item:item['id']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Lectures 2 and 3 added: eight checks, five projects, seven unmodified local mains. Existing files preserved.')

if __name__=='__main__':main()
