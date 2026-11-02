import math
import re

def transformed(sample,mix):
    l,r=sample;a,b,c,d=mix
    return a*l+b*r,c*l+d*r
def power(samples):return sum((l*l+r*r)/2 for l,r in samples)/len(samples) if samples else 0.0
def scenario(name,samples,first,second,critical=False):
    source=str(len(samples))+'\n'+'\n'.join(f'({l},{r})' for l,r in samples)+f'\n[[{first[0]},{first[1]}],[{first[2]},{first[3]}]]\n[[{second[0]},{second[1]}],[{second[2]},{second[3]}]]\n'
    result=[transformed(transformed(s,first),second) for s in samples]
    return dict(name=name,input=source,valid=True,count=len(samples),input_power=power(samples),output_power=power(result),first=result[0] if result else None,last=result[-1] if result else None,category='composition',critical=critical,weight=2 if critical else 1)
def cases():
    identity=(1,0,0,1);swap=(0,1,1,0)
    good=[
        scenario('Пустая запись',[],identity,swap),
        scenario('Один отсчёт и единичные преобразования',[(1,2)],identity,identity),
        scenario('Некоммутирующие преобразования, полный блок',[(1,2),(-3,4),(0.5,-1),(2,-2)],(2,0,0,3),swap,True),
        scenario('Отрицательные и несимметричные коэффициенты',[(-2,3),(4,-1)],(1,-2,0.5,-1),(-3,1,2,0.25),True),
        scenario('Первое преобразование единичное',[(2,-5),(-1,3)],identity,(2,-1,3,1)),
        scenario('Мощность считается после обоих преобразований',[(0.1,0.2),(0.3,-0.4),(1.25,2.5)],(1.5,0.25,-0.5,2),(-2,1,3,0.5),True),
        scenario('Первый и последний относятся к результату',[(1,0),(2,1),(3,-2),(4,3)],(1,2,3,4),(-1,0,0,2),True),
    ]
    bad=[('-1\n','Отрицательное N'),('5\n','N превышает ёмкость'),('bad\n','N не является целым'),('1\n(1;2)\n[[1,0],[0,1]]\n[[1,0],[0,1]]\n','Неверный формат отсчёта'),('1\n(1,2)\n[[1,0],[0,1]]\n[[1,0],[0,1)\n','Ошибка в последнем микшере'),('1\n(1,2)\n[[1,0],[0,1]]\n','Неполный сценарий')]
    return good+[dict(name=n,input=i,valid=False,category='negative',critical=True,weight=1) for i,n in bad]

def evaluate(case,run):
    stdout=run['output'];stderr=run.get('stderr','')
    if not case['valid']:
        ok=run['code']!=0 and not stdout.strip() and bool(stderr.strip()) and not run['timeout']
        return ok, 'Ошибка должна дать ненулевой код и диагностику в stderr, без частичного отчёта в stdout.' if not ok else ''
    if run['code']!=0:return False,'Ожидался успешный сценарий с нулевым кодом завершения.'
    lines=stdout.strip().splitlines()
    if len(lines)!=5:return False,'Успешный отчёт должен содержать ровно пять строк установленного формата.'
    expected=['count','input_power','output_power','first','last'];values={}
    for line,key in zip(lines,expected):
        if not line.startswith(key+'='):return False,'Нарушены имена или порядок полей отчёта.'
        values[key]=line[len(key)+1:]
    try:
        if int(values['count'])!=case['count']:return False,'count не совпадает с числом отсчётов.'
        for key in ('input_power','output_power'):
            value=float(values[key])
            if not math.isfinite(value) or abs(value-case[key])>1e-9:return False,f'{key}: неверная формула, порядок преобразований или недостаточная точность.'
        for key in ('first','last'):
            if case[key] is None:
                if values[key]!='none':return False,'Пустой блок должен давать first=none и last=none.'
            else:
                match=re.fullmatch(r'\(\s*([^,]+),\s*([^,]+)\)',values[key])
                if not match:return False,'Крайний отсчёт должен иметь формат (L,R).'
                actual=tuple(float(x) for x in match.groups())
                if any(not math.isfinite(a) or abs(a-b)>1e-9 for a,b in zip(actual,case[key])):return False,f'{key} должен относиться к преобразованной последовательности.'
    except (ValueError,OverflowError):return False,'Поля отчёта содержат недопустимые числовые значения.'
    return True,''
