import {Markdown} from '../theory/Markdown';

export default function LocalCommands({filename}:{filename:string}){
  const memory=filename!=='MAIN_COLLECTION_LAB.cpp';
  return <details className="pack-local-commands">
    <summary>Команды для локального терминала</summary>
    <p>Поместите выбранный MAIN рядом со своим заголовком .hpp. GCC/Clang должны быть установлены на вашем компьютере. Каждый MAIN компилируется отдельно.</p>
    <h4>Windows PowerShell, GCC/MinGW</h4>
    <Markdown source={'```powershell\ng++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic -Werror '+filename+' -o local_check.exe\n.\\local_check.exe\n```'}/>
    <h4>Linux / macOS, GCC или Clang</h4>
    <Markdown source={'```bash\ng++ -std=c++17 -Wall -Wextra -Wconversion -Wpedantic -Werror '+filename+' -o local_check\n./local_check\n```'}/>
    <p>Для Clang замените g++ на clang++. Определения методов шаблонов должны быть доступны из заголовка или подключаемого .tpp. Не задавайте NDEBUG.</p>
    {memory&&<><h4>Необязательная проверка памяти</h4><p>Если ваш компилятор поддерживает санитайзеры, выполните отдельную сборку. Приведён запуск для Linux/macOS; в Windows используйте имя .exe.</p><Markdown source={'```bash\ng++ -std=c++17 -g -fsanitize=address,undefined -fno-omit-frame-pointer '+filename+' -o memory_check\n./memory_check\n```'}/></>}
  </details>;
}
