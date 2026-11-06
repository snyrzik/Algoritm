"""Integrate lecture four from its original local pack; never touch learner files."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT
from tools.prepare_lectures23 import block,write

SOURCE=ROOT/'content/lecture-04/lecture-04'
DEST=ROOT/'days/day-04-lists/lectures/lecture-04'
TITLE='Лекция № 4. Списки, STL-контейнеры и сложность'
ATTRIBUTION='Материал по презентации Е. В. Мясникова «Списки», 49 слайдов. Указание источника сохранено из предоставленного пакета.'

CHECKS=[
 ('Указатели и голова списка',r'''Разберите намеренно ошибочные фрагменты. Не запускайте их с неверными указателями: сначала проследите состояние памяти на бумаге.

```cpp
struct Node { int value; Node* next; };
void push_front(Node*& head, int value) {
    head = new Node{value, nullptr};
    head->next = head;
}
int pop_front(Node*& head) {
    int value = head->value;
    delete head;
    head = head->next;
    return value;
}
```

Объясните потерю старой цепочки, возможное обращение после освобождения и поведение на пустом списке. Исправьте порядок действий самостоятельно. Покажите состояния для пустого, одноэлементного, двухэлементного и трёхэлементного списка; сформулируйте инвариант после каждой строки.
'''),
 ('Двойные связи и граничные случаи',r'''Исходное состояние:

```text
head -> [10] <-> [20] <-> [30] <- tail
```

Вставьте `15` перед вторым узлом. Заполните четыре изменения связей в 6–12 строках собственного кода, затем удалите первую вершину. Изобразите все `prev/next` после каждой операции. Отдельно покажите удаление последнего и единственного узла: что происходит с `head`, `tail` и размером? Не пишите полный класс проекта.

```cpp
// left указывает на 10, right на 20, added — новый узел со значением 15.
// Запишите четыре необходимые связи самостоятельно.
// Затем запишите удаление головы с проверкой пустого состояния.
```
'''),
 ('Контейнер и итератор',r'''Выберите контейнер и обоснуйте компромиссы в трёх ситуациях:

1. Часто читать по индексу и дописывать в конец.
2. Часто вставлять и удалять при уже известной позиции, сохраняя ссылки на другие элементы.
3. Работать с обоими концами и иногда читать по индексу.

Исправьте два коротких ошибочных фрагмента. Объясните, когда и почему сохранённый итератор становится недействительным.

```cpp
std::list<int> values{10, 20, 30};
std::cout << values[1]; // Требуется корректный способ доступа.
```

```cpp
std::vector<int> values{10, 20, 30};
auto saved = values.begin();
values.push_back(40); // Ёмкости может не хватить.
std::cout << *saved;
```

Названия контейнеров без объяснения и исправленных фрагментов недостаточны.
'''),
 ('Стоимость операций',r'''Для каждого фрагмента назовите размер входа, худший случай (либо амортизированную стоимость), число существенных шагов и возможную инвалидацию итераторов. Предполагаются корректные диапазоны; для поиска минимума `n > 0`.

```cpp
// 1. Индексирование, 0 <= index < n.
int value = data[index];

// 2. Поиск первого совпадения.
std::size_t i = 0;
while (i < n && data[i] != target) ++i;

// 3. Минимум без сортировки.
int smallest = data[0];
for (std::size_t j = 1; j < n; ++j)
    if (data[j] < smallest) smallest = data[j];

// 4. Два вложенных цикла.
for (std::size_t row = 0; row < n; ++row)
    for (std::size_t col = 0; col < n; ++col)
        visit(row, col);

// 5. Длинная серия добавлений: разберите отдельный вызов и всю серию.
std::vector<int> values;
for (std::size_t j = 0; j < n; ++j) values.push_back(42);
```

Считайте `visit` и операции над `int` константными по стоимости. Завершите ответ выбором между `vector`, `list`, `deque` для своего сценария и объясните компромиссы. Ответ «так написано в таблице» не является обоснованием.
''')]

PROJECTS=[
 dict(name='ForwardChain<T>',header='forward_chain.hpp',main='MAIN_FORWARD_CHAIN.cpp',
      requirements=['Собственные узлы; STL-контейнеры не заменяют цепочку','Пустой и единственный узел, удаление отсутствующего значения','Дубликаты в начале и середине; удаляется только первое совпадение','Разворот пустого, одноэлементного и длинного списка на месте','Глубокие копии пустого списка и std::string, порядок и самоприсваивание','Инвариант размера, освобождение узлов и исключения при копировании T']),
 dict(name='BidirectionalList<T>',header='bidirectional_list.hpp',main='MAIN_BIDIRECTIONAL_LIST.cpp',
      requirements=['Собственные узлы и согласованные prev/next, head/tail','Смешанная последовательность вставок и удалений; оба конца','Пустой, единственный узел, начало, середина и конец','Индексы на обеих границах и за диапазоном, прямой и обратный доступ','Глубокие копии и std::string, порядок, самоприсваивание и очистка','После каждого изменения сверены size/empty/front/back/at/at_from_back']),
 dict(name='CollectionLab',header='collection_operations.hpp',main='MAIN_COLLECTION_LAB.cpp',
      requirements=['Использованы vector/list/deque и точные контракты четырёх функций','Чётные маркеры не обрабатываются повторно; отрицательные чётные и ноль','Удаление из list итераторным erase; нет разыменования end()','Сдвиг пустого deque, steps == 0 и steps > size()','Слияние отсортированных списков сохраняет дубликаты и исходные аргументы','Пустые контейнеры, отсутствие чётных и все отрицательные значения','Для каждой функции объяснены сложность, корректность итераторов и все семь аналитических вопросов'])]

def numbered_steps(text):
    return re.findall(r'^\d+\. (.+)$',text,re.M)

def main():
    raw=(SOURCE/'LECTURE_04_THEORY.md').read_bytes();theory=raw.decode('utf-8')
    instructions=(SOURCE/'CODEX_INSTRUCTIONS.md').read_bytes().decode('utf-8')
    chapters=list(re.finditer(r'^# Глава [1-4]\..+$',theory,re.M))
    if len(chapters)!=4:raise ValueError('Expected four author chapters')
    manifest=dict(number=4,title=TITLE,attribution=ATTRIBUTION,sourceRoot='content/lecture-04',sourceFilename='LECTURE_04_THEORY.md',sourceSha256=hashlib.sha256(raw).hexdigest(),localInstructionsFilename='MAIN_SYNTAX_CHECK.md',summaryHeading='Основная самостоятельная практика лекции № 4',practiceIntro='Первые два проекта — собственные узлы без STL-контейнеров. CollectionLab специально учит применять vector, list и deque; запрет из ЛР № 1 на него не переносится.',checkIds=[],projectIds=[])
    for index,(title,exercise) in enumerate(CHECKS,1):
        part=theory[chapters[index-1].start():chapters[index].start() if index<4 else theory.index('# Основная самостоятельная практика')]
        author=re.search(r'^### Самостоятельное закрепление.+?(?=\n---|\Z)',part,re.M|re.S)
        if not author:raise ValueError(f'Missing checkpoint {index}')
        key=f'l04-local-c{index:02}'
        task=dict(id=key,day=4,lecture=4,packLecture=4,chapter=index,section='lecture-theory',kind='C',level='A',required=True,version=4,order=10000+index,title=f'Закрепление {index} · {title}',prompt=author[0].rstrip()+'\n\n## Самостоятельная попытка\n\n'+exercise.strip(),minutes=25,tags=['Лекция № 4',title],localAssessment=True,starterFiles={'solution.cpp':'// Короткие исправленные фрагменты. Напишите их самостоятельно.\n'},filePath=f'student/day-04/{key}/solution.cpp',localMains=[],reviewRequirements=['Разобраны все пункты составного закрепления','Записаны собственные исправления и схемы, где они нужны','Есть аргументированное объяснение граничных случаев или сложности'])
        write(task,DEST/'checks'/key);manifest['checkIds'].append(key)
    for index,project in enumerate(PROJECTS,1):
        end=f'## Проект {index+1}.' if index<3 else '# 6.'
        prompt=block(instructions,f'## Проект {index}.',end).rstrip()
        prompt+='\n\n### Самостоятельная реализация\n\n'+manifest['practiceIntro']
        step_heading='### Этапы проекта' if index==1 else '### Этапы'
        steps=numbered_steps(block(prompt,step_heading,'\n### '))
        if not steps:raise ValueError('Missing implementation stages')
        source=(SOURCE/project['main']).read_bytes().decode('utf-8')
        output=re.search(r'std::cout\s*<<\s*"([^"\n]+)"',source)[1].replace('\\n','\n')
        key=f'l04-local-p{index:02}'
        task=dict(id=key,day=4,lecture=4,packLecture=4,section='lecture-practice',kind='C',level='A',required=True,version=4,order=10100+index,title=project['name'],project=project['name'],prompt=prompt,minutes=150,tags=['Лекция № 4','Самостоятельный проект','Сложность операций'],localAssessment=True,starterFiles={project['header']:'// Реализуйте интерфейс самостоятельно. Определения шаблонов доступны в заголовке.\n'},filePath=f'student/day-04/{key}/{project["header"]}',projectSteps=steps,reviewRequirements=['Авторский main запущен со своей реализацией',*project['requirements'],'Записано собственное обоснование сложности'],requiresComplexity=True,trackImplementation=True,localMains=[dict(id=Path(project['main']).stem.lower(),filename=project['main'],sourcePath='lecture-04/'+project['main'],expectedOutput=output)])
        write(task,DEST/'projects'/key);manifest['projectIds'].append(key)
    (DEST/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (DEST.parents[1]/'README.md').write_text('# '+TITLE+'\n\nПолный источник: content/lecture-04/. Четыре главы, четыре закрепления, три самостоятельных проекта.\n\nОткрыть: http://127.0.0.1:8765/#/theory/4/overview\n',encoding='utf-8',newline='\n')
    nav_path=ROOT/'app/src/lectures/catalog.json';navigation=json.loads(nav_path.read_text(encoding='utf-8'))
    navigation=[n for n in navigation if n['number']!=4]+[dict(number=4,title=TITLE,attribution=ATTRIBUTION,chapters=[dict(id=f'chapter-{i+1}',title=m[0][2:].strip()) for i,m in enumerate(chapters)])]
    nav_path.write_text(json.dumps(navigation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    course_path=ROOT/'days/course.json';course=json.loads(course_path.read_text(encoding='utf-8'))
    course=[m for m in course if m['id']!=4]+[dict(id=4,title=TITLE.removeprefix('Лекция № 4. '),subtitle='Собственные узлы, стандартные контейнеры и оценка операций',topics=['Односвязный список','Двусвязный список','STL','Сложность'],duration='В своём темпе')]
    course_path.write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Lecture 4 added: complete source, four checkpoints, three projects, three original mains. Learner files untouched.')

if __name__=='__main__':main()
