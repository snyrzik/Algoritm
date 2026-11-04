import {useCallback,useEffect,useRef,useState} from 'react';
import {api,errorMessage} from '../api';
import type {Detail} from '../types';

export function downloadFile(name:string,text:string,type='text/plain;charset=utf-8'){
 const url=URL.createObjectURL(new Blob([text],{type}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

export function useWorkspace(taskId:string|undefined){
 const [detail,setDetail]=useState<Detail|null>(null),[files,setFiles]=useState<Record<string,string>>({}),[loading,setLoading]=useState(false),[error,setError]=useState(''),[saveState,setSaveState]=useState('Сохранено'),[dirty,setDirty]=useState(false);
 const current=useRef<{id:string;files:Record<string,string>;revision:string;dirty:boolean}|null>(null),pending=useRef<Promise<void>|null>(null),generation=useRef(0);
 const persist=useCallback(async()=>{
   if(pending.current)await pending.current;
   if(!current.current?.dirty)return;
   const save=async()=>{while(current.current?.dirty){const item=current.current,copy={...item.files};setSaveState('Сохраняем…');const result=await api<{revision:string}>('files/'+item.id,{files:copy,revision:item.revision},'PUT');if(current.current!==item)return;item.revision=result.revision;item.dirty=JSON.stringify(copy)!==JSON.stringify(item.files);setDetail(value=>value?.task.id===item.id?{...value,revision:result.revision}:value);if(!item.dirty){localStorage.removeItem('mastery-draft-'+item.id);setDirty(false);setSaveState('Сохранено на компьютере');}}};
   const operation=save();pending.current=operation;
   try{await operation;}catch(e){setSaveState('Черновик сохранён в браузере');setError(errorMessage(e));throw e;}finally{if(pending.current===operation)pending.current=null;}
 },[]);
 useEffect(()=>{const version=++generation.current;if(!taskId){persist().catch(()=>{});return;}setLoading(true);setError('');
  (async()=>{await persist();const data=await api<Detail>('task/'+taskId);if(generation.current!==version)return;let draft:Record<string,string>|null=null;try{const raw=localStorage.getItem('mastery-draft-'+taskId);if(raw){const value=JSON.parse(raw);if(value&&Object.keys(value).sort().join()===Object.keys(data.files).sort().join()&&Object.values(value).every(v=>typeof v==='string'))draft=value;}}catch{/* Disk is authoritative for malformed drafts. */}
    current.current={id:taskId,files:draft||data.files,revision:data.revision,dirty:!!draft};setDetail(data);setFiles(draft||data.files);setDirty(!!draft);setSaveState(draft?'Восстановлен черновик из браузера':'Сохранено на компьютере');if(data.timerError)setError(data.timerError);
  })().catch(e=>{if(generation.current===version)setError(errorMessage(e));}).finally(()=>{if(generation.current===version)setLoading(false);});
 },[taskId,persist]);
 useEffect(()=>{if(!dirty)return;const timer=setTimeout(()=>persist().catch(()=>{}),800);return()=>clearTimeout(timer);},[files,dirty,persist]);
 useEffect(()=>{const before=(event:BeforeUnloadEvent)=>{if(current.current?.dirty){event.preventDefault();event.returnValue='';}};window.addEventListener('beforeunload',before);return()=>window.removeEventListener('beforeunload',before);},[]);
 useEffect(()=>{const focus=()=>{if(!taskId||current.current?.dirty)return;api<Detail>('task/'+taskId).then(data=>{const item=current.current;if(item?.id===data.task.id&&!item.dirty&&item.revision!==data.revision){item.files=data.files;item.revision=data.revision;setDetail(data);setFiles(data.files);setSaveState('Обновлено из IDE');}}).catch(e=>setError(errorMessage(e)));};window.addEventListener('focus',focus);return()=>window.removeEventListener('focus',focus);},[taskId]);
 const edit=useCallback((value:string,name='solution.hpp')=>{const item=current.current;if(!item)return;item.files={...item.files,[name]:value};item.dirty=true;setFiles(item.files);setDirty(true);setSaveState('Есть изменения');try{localStorage.setItem('mastery-draft-'+item.id,JSON.stringify(item.files));}catch{setError('Не удалось сохранить черновик в браузере. Сохраните файл на компьютер.');}},[]);
 const exportDraft=useCallback(()=>{if(current.current)downloadFile(current.current.id+'-draft.json',JSON.stringify(current.current.files,null,2),'application/json');},[]);
 const reload=useCallback(async()=>{const item=current.current;if(!item)return;if(item.dirty)exportDraft();const data=await api<Detail>('task/'+item.id);if(current.current!==item)return;current.current={id:item.id,files:data.files,revision:data.revision,dirty:false};localStorage.removeItem('mastery-draft-'+item.id);setDetail(data);setFiles(data.files);setDirty(false);setError('');setSaveState('Загружена версия с диска');},[exportDraft]);
 return {detail,files,loading,error,setError,saveState,dirty,edit,persist,reload,exportDraft};
}
