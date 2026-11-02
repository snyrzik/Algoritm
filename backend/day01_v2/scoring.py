import copy
import re
from .. import storage
from ..catalog import catalog

def with_variant(task,number=0):
    if type(number) is not int or number<0 or number>len(task.get('variants',[])):raise ValueError('Неизвестный вариант повторения')
    result=copy.deepcopy(task);result['variant']=number
    if number:
        result.update(task['variants'][number-1])
        original=task['explanation']
        maps=[{'4':'9','7':'12'},{'4':'2','9':'6'},{'5':'11','6':'12','7':'13'},{'1':'3','2':'5','3':'8','7':'6'},{'7':'5'},{'12':'15'}]
        mapping=maps[task['number']-1]
        result['explanation']=re.sub(r'\b\d+\b',lambda m:mapping.get(m[0],m[0]),original)
    return result

def prediction(task,body):
    task=with_variant(task,body.get('variant',0))
    output=body.get('output','');text=body.get('explanation','');trace=body.get('trace',{})
    if not isinstance(output,str) or not isinstance(text,str) or not isinstance(trace,dict):raise ValueError('Нужны вывод, объяснение и трассировка')
    if not output.strip():raise ValueError('Запишите ожидаемый вывод')
    if len(text.strip())<15:raise ValueError('Сначала объясните своими словами, какие операции выполняются')
    if set(trace)!=set(task['traceAnswer']):raise ValueError('Заполните все шаги трассировки')
    correct_output=output.replace('\r\n','\n').strip()==task['expectedOutput']
    correct_trace=all(str(trace[k]).strip()==v for k,v in task['traceAnswer'].items())
    points=int(correct_output)+int(correct_trace)
    return dict(status='PASS' if points==2 else 'FAIL',score=points*50,pointsEarned=points,maxPoints=2,mode='answer',variant=task['variant'],outputCorrect=correct_output,traceCorrect=correct_trace,message='Проверены точный вывод и причинная трассировка.',feedback=dict(expectedOutput=task['expectedOutput'],explanation=task['explanation'],trace=[dict(label=field['label'],correct=str(trace.get(field['id'],'')).strip()==task['traceAnswer'][field['id']]) for field in task['traceFields']]),reviewNote='Формулировка свободного объяснения сохранена. Балл за причины опирается на проверяемые состояния и утверждения трассировки; текст не оценивается поиском ключевых слов.')

def diagnosis(task,body):
    text=body.get('explanation','');rules=body.get('rules',[])
    if not isinstance(text,str) or len(text.strip())<15:raise ValueError('Сначала объясните характер дефекта своими словами')
    allowed={x['id'] for x in task['diagnosisChoices']}
    if not isinstance(rules,list) or not rules or any(not isinstance(x,str) or x not in allowed for x in rules):raise ValueError('Отметьте затронутые правила')
    return dict(status='DIAGNOSIS_RECORDED',score=0,mode='diagnosis',diagnosisCorrect=set(rules)==set(task['diagnosisAnswer']),explanation=text,rules=rules,message='Разбор зафиксирован. Теперь исправьте код и подтвердите поведение тестами.',reviewNote='Проверяется соответствие выбранных правил конкретному контракту. Свободное объяснение сохранено для содержательного разбора.')

def latest_diagnosis(task_id):
    return next((a for a in storage.history(task_id) if a['mode']=='diagnosis'),None)

def summary():
    tasks=[t for t in catalog() if t.get('version')==2]
    attempts=storage.history();latest={}
    for attempt in attempts:
        if attempt['mode'] not in ('answer','test'):continue
        if attempt['task'] not in latest:latest[attempt['task']]=attempt
    earned=sum(float(latest.get(t['id'],{}).get('pointsEarned',0)) for t in tasks)
    groups=[]
    for group in ('Q','S','P','D','A','B','C'):
        items=[t for t in tasks if t['group']==group]
        maximum=sum(t['maxPoints'] for t in items)
        points=sum(float(latest.get(t['id'],{}).get('pointsEarned',0)) for t in items)
        groups.append(dict(id=group,maximum=maximum,earned=round(points,2),passed=sum(latest.get(t['id'],{}).get('status')=='PASS' for t in items),total=len(items)))
    critical=[]
    for task in tasks:
        result=latest.get(task['id'],{})
        if task['group']=='A' and not result.get('compiled'):critical.append(dict(task=task['id'],message=f"{task['title']}: обязательная реализация ещё не собрана"))
        if task['group'] in ('A','B') and result.get('status')!='PASS':critical.append(dict(task=task['id'],message=f"{task['title']}: для полного зачёта нужны все обязательные проверки"))
        for failure in result.get('criticalFailures',[]):critical.append(dict(task=task['id'],message=failure))
    c=next((t for t in tasks if t['group']=='C'),None)
    if c and latest.get(c['id'],{}).get('status')!='PASS':critical.append(dict(task=c['id'],message='C1 ещё не выполнена: уверенное практическое владение не подтверждено'))
    all_pass=bool(tasks) and all(latest.get(t['id'],{}).get('status')=='PASS' for t in tasks)
    baseline=all(latest.get(t['id'],{}).get('status')=='PASS' for t in tasks if t['group'] in ('A','B')) and bool(tasks)
    state='Полный автоматический зачёт' if all_pass and not critical else 'Пройден базовый уровень' if baseline else 'Практика не завершена'
    return dict(version=2,maximum=130,earned=round(earned,2),percent=round(earned/130*100,1),groups=groups,critical=critical,state=state,passed=sum(latest.get(t['id'],{}).get('status')=='PASS' for t in tasks),total=len(tasks),compileRuns=sum(a['mode']=='compile' and a['task'].startswith('d01-v2-') for a in attempts),testRuns=sum(a['mode']=='test' and a['task'].startswith('d01-v2-') for a in attempts))
