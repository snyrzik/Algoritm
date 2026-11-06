import {useEffect,useState} from 'react';
import {Download} from 'lucide-react';
import {api,errorMessage} from '../api';
import {type Attempt,statusNames} from '../types';

export default function SavedWork(){
 const [items,setItems]=useState<{id:string;title:string;day:number;attempts:Attempt[];hasFiles:boolean}[]>([]),[error,setError]=useState('');
 useEffect(()=>{let active=true;api<typeof items>('saved-work').then(value=>{if(active)setItems(value);}).catch(e=>{if(active)setError(errorMessage(e));});return()=>{active=false;};},[]);
 if(!items.length&&!error)return null;
 return <section className="platform-saved-work"><div className="platform-section-heading"><div><h2>Мои ранее сохранённые решения</h2><p>Старые учебные задания удалены. Ваши файлы и результаты сохранены отдельно от новой программы.</p></div><a className="pack-download-button" href="/api/saved-work-bundle" download="my-earlier-work.zip"><Download size={15}/>Скачать мои файлы и результаты</a></div>{error&&<p role="alert">{error}</p>}<details><summary>Сохранённые исходники и история ({items.length})</summary>{items.map(item=><div className="platform-saved-work-row" key={item.id}><span>{item.title}<small>Модуль {item.day} · {item.id}</small></span><span>{item.attempts.length?statusNames[item.attempts[0].status]||item.attempts[0].status:'Исходники сохранены'}</span></div>)}</details></section>;
}
