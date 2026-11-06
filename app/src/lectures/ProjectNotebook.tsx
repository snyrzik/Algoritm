import type {Task} from '../types';

export interface NotebookState {
  implementation?:number[];
  compileNotes?:string;
  reviewNotes?:string;
  complexityNotes?:string;
}

export default function ProjectNotebook({task,value,onChange}:{task:Task;value:NotebookState;onChange:(value:Partial<NotebookState>)=>void}){
  return <section className="pack-project-notebook" aria-label="Ход самостоятельной работы">
    {task.trackImplementation&&<fieldset className="pack-requirements pack-implementation">
      <legend>Этапы реализации</legend>
      {task.projectSteps?.map((step,index)=><label key={step}>
        <input type="checkbox" checked={value.implementation?.includes(index)||false} onChange={event=>onChange({implementation:event.target.checked?[...(value.implementation||[]),index]:(value.implementation||[]).filter(item=>item!==index)})}/>
        <span>{index+1}. {step}</span>
      </label>)}
    </fieldset>}
    <label className="pack-field">Проблемы компиляции<textarea aria-label="Проблемы компиляции" value={value.compileNotes||''} onChange={event=>onChange({compileNotes:event.target.value})} placeholder="Сообщения локального компилятора и что удалось исправить"/></label>
    <label className="pack-field">Замечания при ревью<textarea aria-label="Замечания при ревью" value={value.reviewNotes||''} onChange={event=>onChange({reviewNotes:event.target.value})} placeholder="Инварианты, указатели, итераторы и замечания к своему коду"/></label>
    {task.requiresComplexity&&<label className="pack-field">Обоснование сложности (часть проекта)<textarea aria-label="Обоснование сложности" value={value.complexityNotes||''} onChange={event=>onChange({complexityNotes:event.target.value})} placeholder="Назовите размер входа, оценку ключевых операций и объясните число шагов в своей реализации"/></label>}
    <p>Сохраняйте этапы и заметки кнопкой «Сохранить ход работы». Итоговую отметку поставьте после локальных и дополнительных граничных проверок.</p>
  </section>;
}
