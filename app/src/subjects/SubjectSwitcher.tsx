export default function SubjectSwitcher({current,navigate}:{current:'cpp'|'python';navigate?:(path:string)=>unknown}){
  return <label className="subject-switcher">Предмет
    <select aria-label="Выбрать предмет" value={current} onChange={event=>{const path=event.target.value==='python'?'python':'home';if(navigate)navigate(path);else location.hash='/'+path;}}>
      <option value="cpp">C++ · Алгоритмы и структуры</option>
      <option value="python">Python Recall · Повторение</option>
    </select>
  </label>;
}
