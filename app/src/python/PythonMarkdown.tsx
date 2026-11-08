import {useMemo,useState,type ReactNode} from 'react';
import ReactMarkdown,{type Components} from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {pythonLanguage} from '@codemirror/lang-python';
import {highlightTree,classHighlighter} from '@lezer/highlight';
import {Copy,Check} from 'lucide-react';
import '../theory/theory.css';

function Code({language,value}:{language:string;value:string}){
 const [copied,setCopied]=useState(false),[error,setError]=useState('');
 const content=useMemo(()=>{if(!['python','py'].includes(language))return value;const spans:ReactNode[]=[];let end=0;highlightTree(pythonLanguage.parser.parse(value),classHighlighter,(from,to,classes)=>{if(from>end)spans.push(value.slice(end,from));spans.push(<span className={classes} key={from}>{value.slice(from,to)}</span>);end=to;});if(end<value.length)spans.push(value.slice(end));return spans;},[language,value]);
 return <figure className="theory-code-block"><div className="theory-code-toolbar"><span>{['python','py'].includes(language)?'Python':'Пример / локальный терминал'}</span><button onClick={async()=>{try{await navigator.clipboard.writeText(value);setCopied(true);}catch{setError('Копирование недоступно');}}}>{copied?<Check size={14}/>:<Copy size={14}/>} {error|| (copied?'Скопировано':'Копировать')}</button></div><pre tabIndex={0}><code className={'language-'+language}>{content}</code></pre></figure>;
}
const components:Components={pre:({children})=><>{children}</>,code:({className,children})=>{const language=/language-(\S+)/.exec(className||'')?.[1];return language?<Code language={language} value={String(children)}/>:<code>{children}</code>;},table:({children})=><div className="theory-table-scroll"><table>{children}</table></div>,a:({href,children})=><a href={href} target="_blank" rel="noreferrer">{children}</a>};
export default function PythonMarkdown({source}:{source:string}){
 // Python special method names in ordinary prose must not become Markdown emphasis.
 const text=source.split(/(```[\s\S]*?```|`[^`\n]+`)/g).map((part,index)=>index%2?part:part.replace(/__[A-Za-z][A-Za-z0-9_]*__/g,name=>'`'+name+'`')).join('');
 return <div className="theory-markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>{text}</ReactMarkdown></div>;
}
