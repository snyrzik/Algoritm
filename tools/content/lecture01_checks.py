"""Local check scenarios. No class implementations."""
def test(name, code, category='functional'):
    return dict(name=name, code=code, category=category)

SCORE = [
    test('Нулевой счётчик и чтение const', 'const ScoreCounter zero; const ScoreCounter other(17); CHECK(std::invoke(mastery_check::score_read,zero)==0); CHECK(std::invoke(mastery_check::score_read,other)==17);', 'boundary'),
    test('Произвольное положительное и отрицательное изменение', 'ScoreCounter s(10); std::invoke(mastery_check::score_add,s,7); CHECK(std::invoke(mastery_check::score_read,s)==17); std::invoke(mastery_check::score_add,s,-25); CHECK(std::invoke(mastery_check::score_read,s)==-8); std::invoke(mastery_check::score_add,s,0); CHECK(std::invoke(mastery_check::score_read,s)==-8);'),
    test('Цепочка возвращает исходный объект', 'ScoreCounter s(3); auto& first=std::invoke(mastery_check::score_add,s,2); CHECK(&first==&s); auto& second=std::invoke(mastery_check::score_add,first,4); CHECK(&second==&s && std::invoke(mastery_check::score_read,s)==9);', 'types'),
    test('higher_score: больше, меньше и равенство', 'const ScoreCounter a(12),b(5),c(12); CHECK(higher_score(a,b)); CHECK(!higher_score(b,a)); CHECK(!higher_score(a,c)); CHECK(std::invoke(mastery_check::score_read,a)==12 && std::invoke(mastery_check::score_read,b)==5);'),
    test('Сравнение отрицательных значений', 'const ScoreCounter a(-2),b(-10); CHECK(higher_score(a,b)); CHECK(!higher_score(b,a));'),
    test('Независимость копирующего конструктора', 'ScoreCounter a(20); ScoreCounter b(a); std::invoke(mastery_check::score_add,b,15); CHECK(std::invoke(mastery_check::score_read,a)==20 && std::invoke(mastery_check::score_read,b)==35);'),
    test('Копия живёт после оригинала', 'ScoreCounter* copy=nullptr; {const ScoreCounter original(44); copy=new ScoreCounter(original);} CHECK(std::invoke(mastery_check::score_read,*copy)==44); delete copy;', 'lifetime'),
]
SCORE_TYPES = '''
static_assert(std::is_member_function_pointer_v<decltype(mastery_check::score_read)>, "Bind your reading METHOD in test_adapter.hpp");
static_assert(std::is_member_function_pointer_v<decltype(mastery_check::score_add)>, "Bind your modifying METHOD in test_adapter.hpp");
static_assert(std::is_invocable_v<decltype(mastery_check::score_read),const ScoreCounter&>, "Reading must work on const objects");
static_assert(std::is_integral_v<std::remove_cv_t<std::remove_reference_t<std::invoke_result_t<decltype(mastery_check::score_read),const ScoreCounter&>>>>);
static_assert(std::is_same_v<std::invoke_result_t<decltype(mastery_check::score_add),ScoreCounter&,int>,ScoreCounter&>, "Chain must return ScoreCounter&");
using HigherScoreSignature = bool (*)(const ScoreCounter&,const ScoreCounter&);
static_assert(std::is_same_v<decltype(static_cast<HigherScoreSignature>(&higher_score)),HigherScoreSignature>, "Compare without copying the parameters");
'''
DURATION = [
    test('Секунды и const-чтение', 'const Duration zero(0),negative(-7),positive(61); CHECK(std::invoke(mastery_check::duration_read,zero)==0); CHECK(std::invoke(mastery_check::duration_read,negative)==-7); CHECK(std::invoke(mastery_check::duration_read,positive)==61);', 'boundary'),
    test('59 + 61, исходные операнды неизменны', 'const Duration a(59),b(61); const Duration c=a+b; CHECK(std::invoke(mastery_check::duration_read,c)==120); CHECK(std::invoke(mastery_check::duration_read,a)==59 && std::invoke(mastery_check::duration_read,b)==61);'),
    test('Цепочка += меняет именно a', 'Duration a(59); const Duration b(61); CHECK(&((a+=b)+=Duration(3))==&a); CHECK(std::invoke(mastery_check::duration_read,a)==123 && std::invoke(mastery_check::duration_read,b)==61);', 'types'),
    test('Сложение отрицательных длительностей', 'CHECK(std::invoke(mastery_check::duration_read,Duration(-15)+Duration(7))==-8); CHECK(std::invoke(mastery_check::duration_read,Duration(-15)+Duration(-7))==-22); CHECK(std::invoke(mastery_check::duration_read,Duration(7)+Duration(-7))==0);'),
    test('Унарный минус не меняет операнд', 'const Duration a(-12); CHECK(std::invoke(mastery_check::duration_read,-a)==12); CHECK(std::invoke(mastery_check::duration_read,a)==-12); CHECK(std::invoke(mastery_check::duration_read,-Duration(0))==0);'),
    test('== и != согласованы', 'const Duration a(17),b(17),c(-17); CHECK(a==b && !(a!=b)); CHECK(a!=c && !(a==c)); CHECK(a==a);'),
    test('Префиксный ++: новое значение и ссылка', 'Duration value(7); Duration& result=++value; CHECK(&result==&value); CHECK(std::invoke(mastery_check::duration_read,value)==8 && std::invoke(mastery_check::duration_read,result)==8);', 'types'),
    test('Постфиксный ++: независимое старое значение', 'Duration value(8); Duration before=value++; CHECK(std::invoke(mastery_check::duration_read,before)==8 && std::invoke(mastery_check::duration_read,value)==9); ++value; CHECK(std::invoke(mastery_check::duration_read,before)==8);'),
    test('Сценарий из условия: сначала ++, затем ++(int)', 'Duration value(7); Duration first=++value; Duration second=value++; CHECK(std::invoke(mastery_check::duration_read,first)==8); CHECK(std::invoke(mastery_check::duration_read,second)==8); CHECK(std::invoke(mastery_check::duration_read,value)==9);'),
    test('Самосложение и переход через ноль', 'Duration value(-1); CHECK(&(value+=value)==&value); CHECK(std::invoke(mastery_check::duration_read,value)==-2); ++value; value++; CHECK(std::invoke(mastery_check::duration_read,value)==0);'),
]
DURATION_TYPES = '''
static_assert(std::is_member_function_pointer_v<decltype(mastery_check::duration_read)>);
static_assert(std::is_invocable_v<decltype(mastery_check::duration_read),const Duration&>);
static_assert(std::is_integral_v<std::remove_cv_t<std::remove_reference_t<std::invoke_result_t<decltype(mastery_check::duration_read),const Duration&>>>>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()+std::declval<const Duration&>()),Duration>);
static_assert(std::is_same_v<decltype(std::declval<Duration&>()+=std::declval<const Duration&>()),Duration&>);
static_assert(std::is_same_v<decltype(-std::declval<const Duration&>()),Duration>);
static_assert(std::is_same_v<decltype(++std::declval<Duration&>()),Duration&>);
static_assert(std::is_same_v<decltype(std::declval<Duration&>()++),Duration>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()==std::declval<const Duration&>()),bool>);
static_assert(std::is_same_v<decltype(std::declval<const Duration&>()!=std::declval<const Duration&>()),bool>);
'''
HISTORY = [
    test('Четыре начальных значения', 'const FixedHistory h(10,-20,30,0); CHECK(h[0]==10 && h[1]==-20 && h[2]==30 && h[3]==0);'),
    test('Изменяемый индекс возвращает живой элемент', 'FixedHistory h(1,2,3,4); int& element=h[2]; element=100; CHECK(h[2]==100); h[2]=77; CHECK(element==77);', 'types'),
    test('const-чтение наблюдает оригинал', 'FixedHistory h(1,2,3,4); const FixedHistory& read=h; h[1]=55; CHECK(read[1]==55 && read[0]==1);'),
    test('operator() суммирует, но не изменяет', 'const FixedHistory h(2,5,-7,11); CHECK(h(0,3)==13 && h(1,2)==-2 && h(3,3)==22); CHECK(h[0]==2 && h[3]==11);'),
    test('Перестановка крайних и средних элементов', 'FixedHistory h(1,2,3,4); h.swap_indices(0,3); CHECK(h[0]==4 && h[3]==1); h.swap_indices(1,2); CHECK(h[1]==3 && h[2]==2);'),
    test('Одинаковые индексы допустимы', 'FixedHistory h(1,2,3,4); h.swap_indices(2,2); CHECK(h[0]==1 && h[1]==2 && h[2]==3 && h[3]==4);', 'boundary'),
    test('Недопустимый изменяемый индекс', 'FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{h[4]=99;}); expect_throw<std::out_of_range>([&]{(void)h[9];}); CHECK(h[0]==1 && h[3]==4);', 'negative'),
    test('Недопустимый const-индекс', 'const FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{(void)h[4];});', 'negative'),
    test('Проверяются оба индекса суммы', 'const FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{(void)h(4,0);}); expect_throw<std::out_of_range>([&]{(void)h(0,4);});', 'negative'),
    test('Ошибка второго индекса не меняет ни один элемент', 'FixedHistory h(1,2,3,4); expect_throw<std::out_of_range>([&]{h.swap_indices(1,4);}); CHECK(h[0]==1 && h[1]==2 && h[2]==3 && h[3]==4); expect_throw<std::out_of_range>([&]{h.swap_indices(4,1);}); CHECK(h[1]==2);', 'exception'),
    test('Независимость копий', 'FixedHistory h(1,2,3,4); auto copy=h; copy[0]=99; CHECK(h[0]==1 && copy[0]==99);'),
    test('Обычный массив без динамического выделения', 'const long before=mastery_memory::live; {FixedHistory h(1,2,3,4); CHECK(mastery_memory::live==before); h.swap_indices(0,3); CHECK(mastery_memory::live==before);} CHECK(mastery_memory::live==before);', 'storage'),
]
HISTORY_TYPES = '''
static_assert(std::is_same_v<decltype(std::declval<FixedHistory&>()[0]),int&>);
static_assert(std::is_same_v<std::remove_cv_t<std::remove_reference_t<decltype(std::declval<const FixedHistory&>()[0])>>,int>);
static_assert(!std::is_assignable_v<decltype(std::declval<const FixedHistory&>()[0]),int>, "Const object must not expose writable elements");
static_assert(std::is_same_v<decltype(std::declval<const FixedHistory&>()(0,1)),int>);
'''
CLOCK = [
    test('Точный вывод: 07:05 и 23:59', 'std::ostringstream out; const ClockTime a(7,5),b(23,59); CHECK(&(out<<a)==&out); out<<" | "<<b; CHECK(out.str()=="07:05 | 23:59");', 'io'),
    test('Ведущие нули и крайние значения', 'for(const auto& input:{std::pair<int,int>{0,0},{0,9},{9,0},{12,0}}){std::ostringstream out; out<<ClockTime(input.first,input.second); const std::string s=out.str(); CHECK(s.size()==5 && s[2]==\':\');} std::ostringstream out; out<<ClockTime(0,0); CHECK(out.str()=="00:00");', 'boundary'),
    test('Недопустимый конструктор не создаёт объект', 'for(const auto& p:{std::pair<int,int>{24,0},{-1,0},{12,60},{12,-1}}){bool caught=false; try{ClockTime value(p.first,p.second);(void)value;}catch(const std::invalid_argument&){caught=true;}catch(const std::out_of_range&){caught=true;}CHECK(caught);}', 'negative'),
    test('Правильное чтение и возврат исходного потока', 'std::istringstream in("07:05"); ClockTime value(1,2); CHECK(&(in>>value)==&in && !in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="07:05");', 'io'),
    test('Последовательное чтение двух объектов', 'std::istringstream in(" 07:05 23:59"); ClockTime a(1,1),b(2,2); in>>a>>b; CHECK(!in.fail()); std::ostringstream out; out<<a<<" | "<<b; CHECK(out.str()=="07:05 | 23:59");', 'io'),
    test('24:00 и 12:60 отвергаются с откатом', 'for(const char* input:{"24:00","12:60"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}', 'negative'),
    test('Неправильный разделитель и незавершённое значение', 'for(const char* input:{"12;30","12:","12","",":30","xx:10"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}', 'negative'),
    test('Строгая ширина HH:MM', 'for(const char* input:{"7:05","07:5","-1:30","12:-1"}){ClockTime value(9,45); std::istringstream in(input); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");}', 'negative'),
    test('Частичный разбор не меняет часы', 'ClockTime value(9,45); std::istringstream in("17:wrong"); in>>value; CHECK(in.fail()); std::ostringstream out; out<<value; CHECK(out.str()=="09:45");', 'exception'),
    test('Состояние потокового форматирования сохраняется', 'std::ostringstream out; out.fill(\'*\'); out.precision(3); const auto flags=out.flags(); out<<ClockTime(7,5); CHECK(out.str()=="07:05" && out.fill()==\'*\' && out.precision()==3 && out.flags()==flags); out<<" "<<std::setw(3)<<2; CHECK(out.str()=="07:05 **2");', 'io'),
    test('Ошибка второго чтения сохраняет оба корректных состояния', 'ClockTime a(1,2),b(3,4); std::istringstream in("08:09 24:00"); in>>a>>b; CHECK(in.fail()); std::ostringstream out; out<<a<<" | "<<b; CHECK(out.str()=="08:09 | 03:04");', 'exception'),
]
CLOCK_TYPES = '''
static_assert(std::is_same_v<decltype(std::declval<std::ostream&>()<<std::declval<const ClockTime&>()),std::ostream&>);
static_assert(std::is_same_v<decltype(std::declval<std::istream&>()>>std::declval<ClockTime&>()),std::istream&>);
'''
