TASKS=[]

# Small usage probes are available only after explicitly requesting hint level 3.
# They do not contain a target declaration or an implementation of an exercise.
HINT_PROBES={
 'S':{1:'const Score value(3); (void)value.value();',2:'Score value(3); increase_by(value, 2);',3:'const Score a(1), b(2); auto result = a + b;',4:'(a += b) += c;',5:'auto result = 0.5 * value;',6:'const Score a(1), b(2); bool same = (a == b);',7:'out << value << " done";',8:'value[1] = 9;',9:'const Triple& read = value; (void)read[1];',10:'const Quadratic q(1, 2, 3); (void)q(0.5);',11:'auto* original = &value; auto* returned = &(++value);',12:'auto before = value++;',13:'value.reset(0);',14:'auto before = point; in >> point;'},
 'D':{1:'auto result = a + b; // Сравните время жизни result и локальных объектов.',2:'auto* returned = &((a += b) += c);',3:'const Triple& read = value; (void)read[3];',4:'out << value << " done";',5:'auto before = value; in >> value; // Сравните состояния при fail().',6:'Measurement near_zero(0.5e-9);'},
 'A':{1:'sample[0] = 1.5; const auto& read = sample; (void)read[1];',2:'auto composed = (first * second)(sample);',3:'(void)block[block.size()]; // Допустим ли такой логический индекс?'},
 'B':{1:'auto before = value; in >> value; // При fail() сравните объект с before.',2:'bool same = approximately_same(block, block, 0.0);'},
 'C':{1:'std::cerr << "Invalid input\\n";'},
}
def add(group,number,title,prompt,**kwargs):
    kind=group if group in ('Q','S','P','D') else 'C'
    maximum={'Q':1,'S':2,'P':2,'D':3,'A':{1:10,2:7,3:7}.get(number,0),'B':6,'C':20}[group]
    task=dict(id=f'd01-v2-{group.lower()}{number:02}',day=1,version=2,section='stereolab',group=group,kind=kind,level=group if group in 'ABC' else 'A',number=number,title=title,prompt=prompt,maxPoints=maximum,required=True,minutes={'Q':2,'S':5,'P':6,'D':12,'A':40,'B':40,'C':80}[group],order={'Q':0,'S':100,'P':200,'D':300,'A':400,'B':500,'C':600}[group]+number,tags=['StereoLab',{'Q':'Понимание','S':'Синтаксис','P':'Трассировка','D':'Code review','A':'Реализация','B':'Интеграция','C':'Проектирование'}[group]])
    task.update(kwargs)
    task.setdefault('hints',['Сопоставьте контракт с поведением конкретного объекта до и после операции.','Разделите тип результата, константность и факт изменения исходного объекта.','Проверьте граничный сценарий отдельно. Для ссылочного результата сравните адреса, для потока — состояние и прежнее значение объекта.'])
    if group in HINT_PROBES:
        task['hints'][2]='Небольшой фрагмент для собственного теста (это не реализация):\n'+HINT_PROBES[group][number]
    TASKS.append(task);return task
def test(name,body,category='functional',critical=False,weight=1):return dict(name=name,code=body,category=category,critical=critical,weight=weight)
def cpp(group,number,title,prompt,tests,checks='',**kwargs):
    kwargs.setdefault('starter','// StereoLab · День 1, новая практика.\n// Напишите решение самостоятельно. Добавьте нужные заголовки.\n')
    kwargs.setdefault('runner','cpp')
    return add(group,number,title,prompt,tests=tests,checks=checks,**kwargs)

PREAMBLE='''#include <iostream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <type_traits>
#include <limits>
#include <utility>
#include <string>
#include "support.hpp"
inline void require_contract(bool ok,const char* contract){if(!ok)throw std::runtime_error(contract);}
inline bool close_value(double a,double b,double eps=1e-9){return std::abs(a-b)<=eps;}
'''
RULE_OPTIONS=[
    dict(id='lifetime',label='Время жизни объекта и возвращаемого результата'),
    dict(id='identity',label='Ссылочная семантика и изменение исходного объекта'),
    dict(id='const',label='Доступ через константный объект'),
    dict(id='bounds',label='Проверка допустимых индексов'),
    dict(id='stream_type',label='Тип и возвращаемый объект потока'),
    dict(id='transaction',label='Сохранение прежнего состояния при неудаче'),
    dict(id='initialization',label='Инициализация данных до чтения'),
    dict(id='numeric',label='Числовой контракт и погрешность'),
    dict(id='comparison',label='Согласованность операторов сравнения'),
    dict(id='ownership',label='Владение динамическим ресурсом'),
]
