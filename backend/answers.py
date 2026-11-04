"""Answer grading and file revisions; no C++ toolchain dependency."""
import hashlib
import json

def revision(files):
    return hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def grade_answer(task,answer):
    if not isinstance(answer,list) or any(type(x) is not int or x<0 or x>=len(task['options']) for x in answer):raise ValueError('Некорректный список ответов')
    if not answer:raise ValueError('Выберите ответ')
    ok=sorted(set(answer))==sorted(task['answer'])
    return dict(status='PASS' if ok else 'FAIL',score=100 if ok else 0,answer=answer,mode='answer',message='Ответ верный.' if ok else 'Ответ не соответствует контракту C++17.')
