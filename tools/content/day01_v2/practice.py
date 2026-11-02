import re
from .questions import SOURCE
from .common import cpp,test,add

def excerpt(label):
    match=re.search(rf'^### {label}\. (.*?)(?=^### [AB]\d\.|^## |\Z)',SOURCE,re.M|re.S)
    text=match[0].strip()
    text=re.sub(r'\n\*\*Скрытые проверки:\*\*.*?(?=\n\n|\Z)','',text,flags=re.S)
    text=re.sub(r'\n\*\*Не сообщай пользователю готовые сигнатуры\.\*\*[^\n]*','',text)
    return text

A1=[
test('Нулевой и заданный отсчёт','const StereoSample a;const StereoSample b(2,-1);CHECK(a.left()==0 && a.right()==0);CHECK(b.left()==2 && b.right()==-1);','boundary'),
test('Сложение и вычитание без изменения операндов','const StereoSample a(2,-1),b(3,4);CHECK(a+b==StereoSample(5,3));CHECK(a-b==StereoSample(-1,-5));CHECK(a==StereoSample(2,-1) && b==StereoSample(3,4));'),
test('Унарный минус','const StereoSample a(2,-1);CHECK(-a==StereoSample(-2,1));CHECK(a==StereoSample(2,-1));'),
test('Скаляр с обеих сторон','const StereoSample a(1,-2);CHECK(a*0.5==StereoSample(0.5,-1));CHECK(0.5*a==StereoSample(0.5,-1));CHECK(-2.0*a==StereoSample(-2,4));CHECK(0.0*a==StereoSample());'),
test('Цепочки += и -= возвращают исходный объект','StereoSample a(1,2);const StereoSample b(2,3),c(4,5);CHECK(&((a+=b)+=c)==&a && a==StereoSample(7,10));CHECK(&((a-=b)-=c)==&a && a==StereoSample(1,2));','types',True),
test('Самоалиасинг составных операций','StereoSample a(2,-3);a+=a;CHECK(a==StereoSample(4,-6));a-=a;CHECK(a==StereoSample());'),
test('Изменяемая и константная индексация','StereoSample a(1,2);a[1]=7.5;const StereoSample& c=a;CHECK(c[0]==1 && c[1]==7.5);CHECK(&a[0]==&c[0]);','types',True),
test('Обе перегрузки проверяют индекс 2','StereoSample a(1,2);const auto& c=a;expect_throw<std::out_of_range>([&]{a[2]=3;});expect_throw<std::out_of_range>([&]{(void)c[2];});CHECK(a==StereoSample(1,2));','negative',True),
test('Большой недопустимый индекс','const StereoSample a(1,2);expect_throw<std::out_of_range>([&]{(void)a[std::numeric_limits<std::size_t>::max()];});','negative',True),
test('Равенство по абсолютному допуску','CHECK(StereoSample(0,0)==StereoSample(1e-9,-1e-9));CHECK(StereoSample(0,0)!=StereoSample(1.01e-9,0));CHECK(StereoSample(1.1,0)!=StereoSample(1.9,0));CHECK(!(StereoSample(2,3)!=StereoSample(2,3)));','boundary'),
test('Потоковые разделители и цепочки','const StereoSample a(1.25,-2.5),b(3,4);std::ostringstream out;CHECK(&(out<<a)==&out);out<<" | "<<b;std::istringstream in(out.str());char p=0,comma=0,q=0,bar=0;double l=0,r=0;in>>p>>l>>comma>>r>>q>>bar;CHECK(p==char(40) && comma==char(44) && q==char(41) && bar==char(124) && close_value(l,1.25) && close_value(r,-2.5));','io'),
test('Формат double определяется потоком','std::ostringstream out;out<<std::fixed<<std::setprecision(2)<<StereoSample(1.25,-2);CHECK(out.str()=="(1.25,-2.00)");','io'),
test('Независимость обычных копий','StereoSample a(2,3);auto b=a;b[0]=9;CHECK(a.left()==2 && b.left()==9);StereoSample c;c=a;c[1]=7;CHECK(a.right()==3);'),
]
A1_TYPES='''static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>().left()),double> && std::is_same_v<decltype(std::declval<const StereoSample&>().right()),double>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()[0]),double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()[0]),const double&>);
static_assert(std::is_same_v<decltype(std::declval<const StereoSample&>()+std::declval<const StereoSample&>()),StereoSample>);
static_assert(std::is_same_v<decltype(std::declval<StereoSample&>()+=std::declval<const StereoSample&>()),StereoSample&> && std::is_same_v<decltype(std::declval<StereoSample&>()-=std::declval<const StereoSample&>()),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const StereoSample&>()),std::ostream&>);'''
cpp('A',1,'A1 · StereoSample',excerpt('A1'),A1,A1_TYPES,publicChecks=['Арифметика и неизменность операндов','Ссылки, const и цепочки','Индексы и исключения','Допуск и потоковый формат'])

A2=[
test('Единичное преобразование','const ChannelMix id;const StereoSample s(3,-2);auto r=id(s);CHECK(close_value(r.left(),3) && close_value(r.right(),-2));'),
test('Перестановка и независимое усиление','const ChannelMix swap(0,1,1,0),gain(2,0,0,3);const auto a=swap(StereoSample(3,-2));const auto b=gain(StereoSample(1,2));CHECK(close_value(a.left(),-2) && close_value(a.right(),3));CHECK(close_value(b.left(),2) && close_value(b.right(),6));'),
test('Композиция: правое преобразование выполняется первым','const ChannelMix swap(0,1,1,0),gain(2,0,0,3);const StereoSample s(1,2);auto a=(swap*gain)(s),b=(gain*swap)(s);CHECK(close_value(a.left(),6) && close_value(a.right(),2));CHECK(close_value(b.left(),4) && close_value(b.right(),3));','composition',True),
test('Несимметричные коэффициенты композиции','const ChannelMix a(1,2,-3,4),b(2,-1,5,3);CHECK(a*b==ChannelMix(12,5,14,15));CHECK(b*a==ChannelMix(5,0,-4,22));','composition',True),
test('Композиция на нескольких сигналах','const ChannelMix a(1.5,-2,0.25,3),b(-1,4,2,0.5);for(const auto& s:{StereoSample(1,2),StereoSample(-3,0.5),StereoSample(0,0)}){const auto x=(a*b)(s),y=a(b(s));CHECK(close_value(x.left(),y.left()) && close_value(x.right(),y.right()));}','composition',True),
test('Операнды не изменяются','const ChannelMix a(1,2,3,4),b(5,6,7,8);const StereoSample s(2,-1);(void)(a*b);(void)a(s);CHECK(a==ChannelMix(1,2,3,4) && b==ChannelMix(5,6,7,8));CHECK(s.left()==2 && s.right()==-1);'),
test('Равенство всех четырёх коэффициентов','CHECK(ChannelMix(0,0,0,0)==ChannelMix(1e-9,0,0,-1e-9));CHECK(ChannelMix(0,0,0,0)!=ChannelMix(0,0,1.1e-9,0));CHECK(!(ChannelMix()!=ChannelMix()));','boundary'),
test('Потоковый формат матрицы','std::ostringstream out;const ChannelMix a(1.25,-2,3,4);CHECK(&(out<<a)==&out);std::istringstream in(out.str());char x[8]{};double a0=0,b0=0,c0=0,d0=0;in>>x[0]>>x[1]>>a0>>x[2]>>b0>>x[3]>>x[4]>>x[5]>>c0>>x[6]>>d0>>x[7];char last=0;in>>last;CHECK(!in.fail() && close_value(a0,1.25) && b0==-2 && c0==3 && d0==4);CHECK(std::string(x,8)=="[[,],[,]" && last==char(93));','io'),
]
A2_TYPES='''static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()(std::declval<const StereoSample&>())),StereoSample>);
static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()*std::declval<const ChannelMix&>()),ChannelMix>);
static_assert(std::is_same_v<decltype(std::declval<const ChannelMix&>()==std::declval<const ChannelMix&>()),bool>);
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const ChannelMix&>()),std::ostream&>);'''
cpp('A',2,'A2 · ChannelMix',excerpt('A2')+'\n\nДля автономной проверки включите StereoSample.hpp: тип отсчёта предоставляется тестовым окружением с описанными в A1 конструкторами и методами. Эта проверка оценивает только ваш ChannelMix. В B/C будут подключены именно ваши исходники A1.',A2,A2_TYPES,fixtures=['StereoSample'],publicChecks=['Единичность и вызов объекта','Порядок композиции и коэффициенты','const, допуск, потоковый формат'])

A3=[
test('Пустой блок','const AudioBlock b;CHECK(b.size()==0 && b.empty() && !b.full() && b.average_power()==0);','boundary'),
test('Добавление и средняя мощность','AudioBlock b;CHECK(b.append(StereoSample(1,1)) && b.append(StereoSample(3,1)));CHECK(b.size()==2 && !b.empty() && !b.full() && close_value(b.average_power(),3));'),
test('Полная ёмкость и отказ без изменений','AudioBlock b;for(int i=0;i<4;++i)CHECK(b.append(StereoSample(i,-i)));CHECK(b.full() && b.size()==4);CHECK(!b.append(StereoSample(99,99)));for(std::size_t i=0;i<4;++i)CHECK(b[i].left()==static_cast<double>(i));','boundary',True),
test('Проверяются логические, а не физические границы','AudioBlock b;expect_throw<std::out_of_range>([&]{(void)b[0];});b.append(StereoSample(1,2));const AudioBlock& c=b;expect_throw<std::out_of_range>([&]{(void)b[1];});expect_throw<std::out_of_range>([&]{(void)c[3];});','negative',True),
test('Изменяемая ссылка и const-чтение','AudioBlock b;b.append(StereoSample(1,2));b[0][1]=7;const auto& c=b;CHECK(c[0].left()==1 && c[0].right()==7);','types',True),
test('Преобразование возвращает новый блок','AudioBlock b;b.append(StereoSample(1,2));b.append(StereoSample(-3,4));const auto& c=b;const ChannelMix gain(2,0,0,3);auto out=c(gain);CHECK(out.size()==2 && out[0].left()==2 && out[0].right()==6 && out[1].left()==-6 && out[1].right()==12);CHECK(c[0].left()==1 && c[0].right()==2);'),
test('Независимое копирование и присваивание','AudioBlock a;a.append(StereoSample(1,2));auto b=a;b[0][0]=9;CHECK(a[0].left()==1);AudioBlock c;c=a;c[0][1]=8;CHECK(a[0].right()==2);'),
test('Мощность вычисляется по всем логическим элементам','AudioBlock b;b.append(StereoSample(-2,4));CHECK(close_value(b.average_power(),10));b.append(StereoSample(0,0));CHECK(close_value(b.average_power(),5));'),
test('Пустой результат преобразования','const AudioBlock empty;const auto out=empty(ChannelMix(2,3,4,5));CHECK(out.empty() && out.size()==0 && out.average_power()==0);','boundary'),
test('Хранение без собственных динамических аллокаций','const long before=mastery_memory::live;{AudioBlock b;CHECK(b.append(StereoSample(1,2)));CHECK(mastery_memory::live==before);}CHECK(mastery_memory::live==before);','storage',True),
]
A3_TYPES='''static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>().size()),std::size_t>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>()[0]),StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()[0]),const StereoSample&>);
static_assert(std::is_same_v<decltype(std::declval<AudioBlock&>().append(std::declval<const StereoSample&>())),bool>);
static_assert(std::is_same_v<decltype(std::declval<const AudioBlock&>()(std::declval<const ChannelMix&>())),AudioBlock>);'''
cpp('A',3,'A3 · AudioBlock',excerpt('A3')+'\n\nАвтономный тест предоставляет StereoSample.hpp и ChannelMix.hpp. Подключите эти заголовки. Готовые реализации вашего AudioBlock не предоставляются. В B/C эти типы заменяются вашими исходниками A1/A2.',A3,A3_TYPES,fixtures=['StereoSample','ChannelMix'],publicChecks=['Фиксированная ёмкость и отказ append','Логические границы и const','Независимость копий','Преобразование и средняя мощность'])

B1=[
test('Отсчёт: корректный ввод и пробелы','for(const char* s:{"(1.5,-2)","( 1.5 , -2 )"}){StereoSample a(7,8);std::istringstream in(s);CHECK(&(in>>a)==&in && !in.fail() && a==StereoSample(1.5,-2));}','io'),
test('Отсчёт: неверный формат сохраняет прежнее состояние','for(const char* s:{"(1;2)","(1,)","(bad,2)","(1,2","bad",""}){StereoSample a(7,8);std::istringstream in(s);in>>a;CHECK(in.fail() && a==StereoSample(7,8));}','negative',True),
test('Последовательное чтение отсчётов','StereoSample a,b;std::istringstream in("(1,2) (3,4)");in>>a>>b;CHECK(!in.fail() && a==StereoSample(1,2) && b==StereoSample(3,4));','io'),
test('Микшер: правильный ввод и пробелы','for(const char* s:{"[[1,2],[3,4]]","[[ 1 , 2 ], [ 3 , 4 ]]"}){ChannelMix a;std::istringstream in(s);CHECK(&(in>>a)==&in && !in.fail() && a==ChannelMix(1,2,3,4));}','io'),
test('Микшер: скобки, элементы, запятые и откат','for(const char* s:{"[[1,2],(3,4)]","[[1,2],[3]]","[[1;2],[3,4]]","[[1,2],[3,4]","[[1,2],[bad,4]]",""}){ChannelMix a(7,8,9,10);std::istringstream in(s);in>>a;CHECK(in.fail() && a==ChannelMix(7,8,9,10));}','negative',True),
test('Последовательное чтение микшеров','ChannelMix a,b;std::istringstream in("[[1,0],[0,1]] [[2,0],[0,3]]");in>>a>>b;CHECK(!in.fail() && a==ChannelMix() && b==ChannelMix(2,0,0,3));','io'),
test('Успешный первый объект и неудачный второй','StereoSample a(7,8),b(9,10);std::istringstream in("(1,2) (3;4)");in>>a>>b;CHECK(in.fail() && a==StereoSample(1,2) && b==StereoSample(9,10));','negative',True),
]
B1_TYPES='''static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<StereoSample&>()),std::istream&>);
static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<ChannelMix&>()),std::istream&>);'''
cpp('B',1,'B1 · Надёжный потоковый ввод',excerpt('B1')+'\n\nПодключите StereoSample.hpp, ChannelMix.hpp и AudioBlock.hpp. Это ваши исходники A1–A3; платформа берёт их снимки перед проверкой. В условии исходного ТЗ заголовок упоминает три объекта, но перегрузки ввода требуются только для StereoSample и ChannelMix. Ввод или вывод AudioBlock не требуется.',B1,B1_TYPES,dependencies=['d01-v2-a01','d01-v2-a02','d01-v2-a03'],publicChecks=['Два формата и последовательное извлечение','Возврат потока','failbit и полный откат объекта'])

B2=[
test('Фильтр возвращает независимый результат','AudioBlock b;b.append(StereoSample(1,2));auto out=apply_filter(b,ChannelMix(2,0,0,3));CHECK(out[0]==StereoSample(2,6) && b[0]==StereoSample(1,2));'),
test('Цепочка: first, затем second','AudioBlock b;b.append(StereoSample(1,2));b.append(StereoSample(-3,4));const ChannelMix a(2,0,0,3),s(0,1,1,0);auto out=apply_chain(b,a,s);CHECK(out[0]==StereoSample(6,2));CHECK(approximately_same(out,apply_filter(b,s*a),1e-9));CHECK(!approximately_same(out,apply_filter(b,a*s),1e-9));','composition',True),
test('Пустой блок','const AudioBlock b;auto out=apply_chain(b,ChannelMix(),ChannelMix(2,3,4,5));CHECK(out.empty() && approximately_same(b,out,0));','boundary'),
test('Полный блок и порядок элементов','AudioBlock b;for(int i=0;i<4;++i)b.append(StereoSample(i+1,-i));auto out=apply_chain(b,ChannelMix(),ChannelMix(0,1,1,0));CHECK(out.size()==4 && out[3]==StereoSample(-3,4));CHECK(b[3]==StereoSample(4,-3));','boundary'),
test('Разные размеры и нулевой допуск','AudioBlock a,b;a.append(StereoSample(1,2));CHECK(!approximately_same(a,b,1e-9));b.append(StereoSample(1,2));CHECK(approximately_same(a,b,0));b[0][0]+=0.5e-9;CHECK(!approximately_same(a,b,0) && approximately_same(a,b,1e-9));'),
test('Проверяется каждый канал каждого отсчёта','AudioBlock a,b;a.append(StereoSample(1,2));a.append(StereoSample(3,4));b=a;b[1][1]+=0.1;CHECK(!approximately_same(a,b,1e-9));'),
test('Отрицательный epsilon запрещён даже для пустых','const AudioBlock a;expect_throw<std::invalid_argument>([&]{approximately_same(a,a,-1);});','negative',True),
]
B2_TYPES='''using F=AudioBlock(*)(const AudioBlock&,const ChannelMix&);using Chain=AudioBlock(*)(const AudioBlock&,const ChannelMix&,const ChannelMix&);using Same=bool(*)(const AudioBlock&,const AudioBlock&,double);
static_assert(std::is_same_v<decltype(static_cast<F>(&apply_filter)),F> && std::is_same_v<decltype(static_cast<Chain>(&apply_chain)),Chain> && std::is_same_v<decltype(static_cast<Same>(&approximately_same)),Same>);'''
cpp('B',2,'B2 · Композиция фильтров',excerpt('B2')+'\n\nПодключите заголовки StereoSample.hpp, ChannelMix.hpp и AudioBlock.hpp. Используются ваши A1–A3, без подмены чужими реализациями.',B2,B2_TYPES,dependencies=['d01-v2-a01','d01-v2-a02','d01-v2-a03'],publicChecks=['Композиция в правильном порядке','Возврат нового блока','Сравнение всех отсчётов и epsilon'])

C1_PROMPT=SOURCE.split('## 9. C1 — самостоятельный проект дня: `StereoLab Console`',1)[1].split('## 10.',1)[0]
C1_PROMPT=C1_PROMPT.split('Не раскрывай архитектуру решения целиком;',1)[0].strip()
console=add('C',1,'C1 · StereoLab Console',C1_PROMPT+'\n\nПроверяется ваша программа main.cpp. Заголовки StereoSample.hpp / ChannelMix.hpp / AudioBlock.hpp / StereoIO.hpp / StereoPipeline.hpp подключают ваши A1–A3 и B1–B2. До готовности зависимостей сообщается, какого исходника не хватает; готовые решения не подставляются. Для раздельной проверки исключения обработки сценария объявите в solution.hpp функцию int run_stereolab(std::istream&,std::ostream&); она возвращает 0 при успехе, бросает out_of_range для N вне 0..4. main должен её вызвать, обработать ошибки и написать диагностику в cerr. Достаточную точность чисел обеспечьте форматированием потока; фиксированное число знаков не требуется.',runner='console',dependencies=['d01-v2-a01','d01-v2-a02','d01-v2-a03','d01-v2-b01','d01-v2-b02'],starter='// Объявление функции обработки сценария.\n// Реализация — в solution.cpp, main — в main.cpp.\n',starterFiles={'main.cpp':'// Самостоятельная программа StereoLab.\n// Подключите нужные заголовки, напишите main и обработку ошибок.\n'},publicChecks=['Весь сценарий читается до успешного отчёта','Оба преобразования в заданном порядке','Мощности и крайние отсчёты','Ошибки N и формата: stderr и ненулевой код','Независимость копий и согласованный API'])
