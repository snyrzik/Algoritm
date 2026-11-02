import re
from .questions import SOURCE
from .common import cpp,test,RULE_OPTIONS

CASES=[
 [test('Новый результат и сохранение const-операндов','const Score a(2),b(5);const Score c=a+b;CHECK(c.n==7 && a.n==2 && b.n==5);'),test('Независимость результата','Score a(2),b(5);Score c=a+b;c.n=99;CHECK(a.n==2 && b.n==5);')],
 [test('Цепочка меняет именно a','Meter a(1);const Meter b(2),c(4);CHECK(&((a+=b)+=c)==&a && a.value==7);CHECK(b.value==2 && c.value==4);',critical=True),test('Самосложение','Meter a(3);a+=a;CHECK(a.value==6);'),test('Отрицательная прибавка','Meter a(3);a+=Meter(-7);CHECK(a.value==-4);')],
 [test('const-чтение и изменяемый элемент','Triple t;t[1]=9;const Triple& c=t;CHECK(c[1]==9);'),test('Оба варианта защищают границы','Triple t;const Triple& c=t;expect_throw<std::out_of_range>([&]{(void)t[3];});expect_throw<std::out_of_range>([&]{(void)c[3];});CHECK(c[0]==1 && c[1]==2 && c[2]==3);','negative',True),test('Отрицательный индекс','Triple t;expect_throw<std::out_of_range>([&]{(void)t[-1];});','negative',True)],
 [test('Поток и цепочка','const Position p{1,2};std::ostringstream out;CHECK(&(out<<p)==&out);out<<char(33);CHECK(out.str()=="(1,2)!");'),test('Другие значения','std::ostringstream out;out<<Position{-3,0};CHECK(out.str()=="(-3,0)");')],
 [test('Правильный ввод с пробелами','Duo d{7,8};std::istringstream in(" 3 , 4 ");CHECK(&(in>>d)==&in && !in.fail() && d.first==3 && d.second==4);'),test('Неверный разделитель: откат','Duo d{7,8};std::istringstream in("3;4");in>>d;CHECK(in.fail() && d.first==7 && d.second==8);','negative',True),test('Неполное значение и bad: откат','for(const char* s:{"3,","bad"}){Duo d{7,8};std::istringstream in(s);in>>d;CHECK(in.fail() && d.first==7 && d.second==8);}','negative',True)],
 [test('Различные дроби нельзя обрезать до int','const Measurement a(1.1),b(1.9);CHECK(!(a==b) && a!=b);'),test('Абсолютный допуск около нуля','const Measurement a(0),b(0.5e-9),c(2e-9);CHECK(a==b && !(a!=b));CHECK(a!=c && !(a==c));','boundary'),test('Граница допуска','CHECK(Measurement(0)==Measurement(1e-9));CHECK(Measurement(0)!=Measurement(1.01e-9));','boundary')],
]
CHECKS=[
'static_assert(std::is_same_v<decltype(std::declval<const Score&>()+std::declval<const Score&>()),Score>);',
'static_assert(std::is_same_v<decltype(std::declval<Meter&>()+=std::declval<const Meter&>()),Meter&>);',
'static_assert(std::is_same_v<decltype(std::declval<Triple&>()[0]),int&>);static_assert(!std::is_assignable_v<decltype(std::declval<const Triple&>()[0]),int>);',
'static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const Position&>()),std::ostream&>);',
'static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<Duo&>()),std::istream&>);',
'static_assert(std::is_same_v<decltype(std::declval<const Measurement&>()==std::declval<const Measurement&>()),bool>);static_assert(std::is_same_v<decltype(std::declval<const Measurement&>()!=std::declval<const Measurement&>()),bool>);',
]
RULES=[['lifetime'],['identity'],['const','bounds'],['stream_type'],['transaction','initialization'],['numeric','comparison']]
CONTRACTS=[
'Сложение двух const Score создаёт независимое значение суммы; операнды сохраняются.',
'Обычная цепочка составного сложения изменяет исходный левый объект; остальные операнды сохраняются.',
'Triple поддерживает чтение const-объектов и изменение обычных. Параметр индекса остаётся int; допустимы 0,1,2. Другие значения бросают out_of_range до доступа к памяти.',
'Position выводится в любой ostream в формате (x,y); поддержите цепочку вывода.',
'Duo читается в формате a,b с пробелами. При любой неудаче ставится failbit и сохраняются оба прежних значения. Верните переданный поток.',
'Сравнивайте конечные double по абсолютному допуску 1e-9. != согласован с ==; const-объекты поддерживаются. Объясните ограниченность абсолютного допуска и отсутствие универсальной транзитивности.',
]
for number in range(1,7):
    block=re.search(rf'^### D{number:02}\. (.+?)\n(.*?)(?=^### D|^## 7\.)',SOURCE,re.M|re.S)
    source=re.search(r'```cpp\n(.*?)```',block[2],re.S)[1]
    task=cpp('D',number,f'D{number:02} · Code review {number}',CONTRACTS[number-1]+'\n\nСначала объясните характер проблемы в отдельном поле и отметьте затронутые правила. После фиксации разбора исправьте код. Строка с дефектом заранее не отмечается.',CASES[number-1],CHECKS[number-1],starter=source,diagnosisChoices=RULE_OPTIONS,diagnosisAnswer=RULES[number-1],unsafeStarter=number in (1,5),publicChecks=['Диагностика по правилу языка','Корректность исправления','Подтверждённое поведение и границы'])
    task['diagnosisExplanation']=CONTRACTS[number-1]
