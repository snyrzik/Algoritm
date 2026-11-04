import {type Attempt,type Day,type Task,isCompleted} from '../types';

export interface LearningState {bookmarks:string[];lastPath:string}
export type Navigate=(path:string)=>Promise<void>;
export const chapterTitles=['Класс, ссылки, const и копирование','Перегрузка операторов','Индексация и границы','Собственная строка и управление памятью','Потоки и надёжный ввод'];
export const kindTitles={Q:'Вопросы',S:'Синтаксис',P:'Разбор поведения',D:'Исправление кода',C:'Проекты'};
export const moduleTitle=(module:Day)=>module.id===5?'Итоговая практика':module.title;
export function plural(count:number,forms:[string,string,string]){const value=Math.abs(count)%100,last=value%10;return value>10&&value<20?forms[2]:last===1?forms[0]:last>=2&&last<=4?forms[1]:forms[2];}
export function latestAttempts(attempts:Attempt[]){const latest:Record<string,Attempt>={};for(const item of attempts)if(['answer','self-check','test'].includes(item.mode))latest[item.task]??=item;return latest;}
export function taskOrder(a:Task,b:Task){const rank=(t:Task)=>t.section==='lecture-theory'?(t.chapter||0):t.section==='lecture-practice'?100+t.order:t.order;return a.day-b.day||rank(a)-rank(b);}
export function completion(tasks:Task[],latest:Record<string,Attempt>){const required=tasks.filter(t=>t.required);const done=required.filter(t=>isCompleted(latest[t.id])).length;return {done,total:required.length,percent:required.length?(done===required.length?100:Math.min(99,Math.round(done/required.length*100))):0};}
export function nextLesson(tasks:Task[],reading:string[],learning:LearningState,latest:Record<string,Attempt>){
 const path=learning.lastPath;
 if(path.startsWith('task/')){const task=tasks.find(t=>t.id===path.slice(5));if(task&&!isCompleted(latest[task.id]))return {path,title:task.title,caption:`Модуль ${task.day} · продолжить задание`};if(task){const next=tasks.filter(t=>t.day===task.day&&t.required&&!isCompleted(latest[t.id])).sort(taskOrder)[0];if(next)return {path:'task/'+next.id,title:next.title,caption:`Модуль ${next.day} · следующий шаг`};}}
 if(path.startsWith('theory/1/')||!path){const match=/chapter-([1-5])/.exec(path);if(match&&!reading.includes('chapter-'+match[1]))return {path,title:chapterTitles[Number(match[1])-1],caption:'Лекция № 1 · продолжить чтение'};const first=chapterTitles.findIndex((_,i)=>!reading.includes('chapter-'+(i+1)));if(first>=0)return {path:'theory/1/chapter-'+(first+1),title:chapterTitles[first],caption:path?'Лекция № 1 · следующая глава':'Начните с основ'};const next=tasks.filter(t=>t.day===1&&t.required&&!isCompleted(latest[t.id])).sort(taskOrder)[0];if(next)return {path:'task/'+next.id,title:next.title,caption:'Лекция № 1 · самостоятельная работа'};}
 if(/^module\/[2-5]$/.test(path)){const next=tasks.filter(t=>t.day===Number(path.slice(-1))&&t.required&&!isCompleted(latest[t.id])).sort(taskOrder)[0];if(next)return {path:'task/'+next.id,title:next.title,caption:`Модуль ${next.day} · продолжить практику`};}
 const next=tasks.filter(t=>t.required&&!isCompleted(latest[t.id])).sort(taskOrder)[0];return next?{path:next.day===1?'theory/1/overview':'task/'+next.id,title:next.title,caption:`Модуль ${next.day} · следующий шаг`}:{path:'review',title:'Выберите материал для повторения',caption:'Все обязательные задания выполнены'};
}
