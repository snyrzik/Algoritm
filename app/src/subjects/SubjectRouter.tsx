import {lazy,Suspense,useEffect,useState} from 'react';
import './subjects.css';
const Cpp=lazy(()=>import('../App'));
const Python=lazy(()=>import('../python/PythonApp'));
export default function SubjectRouter(){
  const [python,setPython]=useState(()=>/^#\/?python(?:\/|$)/.test(location.hash));
  useEffect(()=>{const change=()=>setPython(/^#\/?python(?:\/|$)/.test(location.hash));window.addEventListener('hashchange',change);return()=>window.removeEventListener('hashchange',change);},[]);
  return <Suspense fallback={<div className="loading-state" role="status">Открываем учебный предмет…</div>}>{python?<Python/>:<Cpp/>}</Suspense>;
}
