import {useEffect,useState} from 'react';
import {BookOpen,Code2,Copy,Download,Check,ArrowRight,Monitor} from 'lucide-react';
import {api,errorMessage} from '../api';
import {type Attempt,type SelfCheckGuide,isCompleted,statusNames} from '../types';
import Theory,{type Lecture} from '../theory/Theory';
import {Markdown} from '../theory/Markdown';
import './lecture01.css';

function download(name:string,value:string){const url=URL.createObjectURL(new Blob([value],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}

export default function Lecture01({section='overview',anchor='',attempts,go,onReading}:{section?:string;anchor?:string;attempts:Attempt[];go:(path:string)=>Promise<void>;onReading?:(reading:string[])=>void}){
 const [lecture,setLecture]=useState<Lecture|null>(null),[selected,setSelected]=useState('l01-v3-p01'),[guide,setGuide]=useState<SelfCheckGuide|null>(null),[error,setError]=useState(''),[copied,setCopied]=useState(false);
 const tab=section==='practice'?'practice':section==='local-checks'?'local-checks':'theory';
 useEffect(()=>{let active=true;api<Lecture>('theory/day-1/lecture-1').then(value=>{if(active)setLecture(value);}).catch(e=>{if(active)setError(errorMessage(e));});return()=>{active=false;};},[]);
 useEffect(()=>{if(tab!=='local-checks')return;let active=true;setGuide(null);setCopied(false);setError('');api<SelfCheckGuide>('self-check/'+selected).then(value=>{if(active)setGuide(value);}).catch(e=>{if(active)setError(errorMessage(e));});return()=>{active=false;};},[selected,tab]);
 const latest:Record<string,Attempt>={};for(const a of attempts)latest[a.task]??=a;
 const projects=lecture?.projects||[];
 const done=projects.filter(t=>isCompleted(latest[t.id])).length;
 const checks=lecture?.checks.filter(t=>isCompleted(latest[t.id])).length||0;
 async function copy(){if(!guide)return;try{await navigator.clipboard.writeText(guide.main);setCopied(true);}catch{setError('Не удалось скопировать. Используйте «Скачать main.cpp».');}}
 return <div className="lecture01-page">
  <header className="lecture01-header"><div><div className="eyebrow">МОДУЛЬ 1 / ЛЕКЦИЯ № 1</div><h1>Перегрузка операций</h1><p>От класса и ссылок — к собственному ресурсу и надёжным потокам.</p></div><span className="lecture01-mode"><Monitor size={16}/>Проверка в своей IDE</span></header>
  <nav className="lecture01-tabs" aria-label="Разделы лекции № 1">{[{id:'theory',label:'Теория',icon:BookOpen,path:'overview'},{id:'practice',label:'Практика',icon:Code2,path:'practice'},{id:'local-checks',label:'Локальная проверка',icon:Monitor,path:'local-checks'}].map(item=><button key={item.id} className={tab===item.id?'active':''} aria-current={tab===item.id?'page':undefined} onClick={()=>go('theory/1/'+item.path)}><item.icon size={17}/>{item.label}</button>)}</nav>
  {error&&<div className="error-banner" role="alert">{error}</div>}
  {tab==='theory'?<Theory section={section} anchor={anchor} attempts={attempts} go={go} onReading={reading=>{setLecture(value=>value?{...value,reading}:value);onReading?.(reading);}}/>:!lecture?<p className="muted">Открываем лекцию…</p>:<>
   <div className="lecture01-stats"><span>Глав прочитано <strong>{lecture.reading.length} / 5</strong></span><span>Закреплений отмечено <strong>{checks} / 5</strong></span><span>Базовых проверок проектов <strong>{done} / 3</strong></span></div>
   {tab==='practice'?<>
    <div className="lecture01-intro"><div className="eyebrow">САМОСТОЯТЕЛЬНАЯ ПРАКТИКА</div><h2>Три проекта с чистого листа</h2><p>Пишите классы в своей IDE. У каждого проекта один готовый main. Успешный запуск подтверждает основные сценарии; память, пограничные случаи и требования ЛР № 1 проверьте отдельно.</p></div>
    <div className="lecture01-projects">{projects.map((task,i)=><article key={task.id} className="lecture01-project"><div className="lecture01-project-number">0{i+1}</div><div><div className="eyebrow">САМОСТОЯТЕЛЬНОЕ ЗАДАНИЕ</div><h2>{task.title}</h2><p>{['Матрица, арифметика, преобразование точки и транзакционный ввод.','Собственный char[], глубокое копирование и операции со строкой.','Произвольная размерность, владение массивом и векторная геометрия.'][i]}</p><span className={'status '+(latest[task.id]?.status||'NEW')}>{latest[task.id]?statusNames[latest[task.id].status]:'Ещё не отмечено'}</span></div><button className="primary" onClick={()=>go('task/'+task.id)}>Условие проекта<ArrowRight size={15}/></button></article>)}</div>
    <details className="lecture01-contract"><summary>Точный API проектов и инструкция из пакета</summary><Markdown source={lecture.localInstructions}/></details>
   </>:<>
    <div className="lecture01-intro"><div className="eyebrow">ЛОКАЛЬНАЯ ПРОВЕРКА</div><h2>Один main для каждого проекта</h2><p>Готовые main из авторского пакета. Сайт не выполняет C++ и не видит результат запуска. После проверки вернитесь в задание и сохраните отметку «Отмечено мной».</p></div>
    <div className="lecture01-project-picker" aria-label="Проект для локальной проверки">{projects.map(task=><button className={selected===task.id?'active':''} key={task.id} onClick={()=>setSelected(task.id)}>{task.title}</button>)}</div>
    {guide?.task===selected&&<section className="lecture01-local-main"><div className="lecture01-main-heading"><h3>{projects.find(t=>t.id===selected)?.project} / main.cpp</h3><div><button onClick={copy}>{copied?<Check size={14}/>:<Copy size={14}/>} {copied?'Скопировано':'Скопировать main'}</button><button onClick={()=>download('main.cpp',guide.main)}><Download size={14}/>Скачать main.cpp</button></div></div><Markdown source={'```cpp\n'+guide.main+'\n```'}/><h3>Ожидаемый вывод</h3><pre className="lecture01-output">{guide.expectedOutput}</pre><p>Программа должна завершиться без ошибки и без срабатывания assert. Не используйте -DNDEBUG. Это базовая проверка, а не полная оценка проекта.</p><button className="primary" onClick={()=>go('task/'+selected)}>Открыть задание и отметить результат<ArrowRight size={15}/></button></section>}
    <section className="lecture01-instructions"><Markdown source={lecture.localInstructions}/></section>
   </>}
  </>}
 </div>;
}
