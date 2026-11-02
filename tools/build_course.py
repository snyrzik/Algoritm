"""Materialize the authored course. Never overwrite a student's existing work."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.content.common import TASKS, TITLES, TOPICS, PREAMBLE
from backend.catalog import ROOT, DAY_NAMES, student_files

def generate():
    from tools.content import questions, syntax, practice, debugging  # noqa: F401
    day01_v2=(ROOT/'days/day-01-operators/practice-v2/manifest.json').exists()
    for task in TASKS:
        if day01_v2 and task['day']==1: continue
        day = ROOT / 'days' / f"day-{task['day']:02}-{DAY_NAMES[task['day']-1]}"
        group = {'Q':'quiz', 'S':'syntax', 'P':'prediction', 'D':'debugging', 'C':'practice'}[task['kind']]
        folder = day / group
        if task['kind']=='C': folder /= task['level']
        folder /= task['id']
        folder.mkdir(parents=True, exist_ok=True)
        task['filePath'] = f"student/day-{task['day']:02}/{task['id']}/solution.hpp"
        (folder / 'exercise.json').write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        markdown=f"# {task['id']} · {task['title']}\n\n{task['prompt']}\n\n" + ('## Проверки\n\n' + '\n'.join('- '+t['name'] for t in task['tests']) if 'tests' in task else '')
        (folder / 'README.md').write_text(markdown.rstrip()+'\n', encoding='utf-8')
        if 'tests' in task:
            tests_dir = day / 'tests'
            tests_dir.mkdir(exist_ok=True)
            snippets = '\n'.join(f'void test_{i}() {{\n{t["code"]}\n}}' for i,t in enumerate(task['tests']))
            snippets = re.sub(r'\b(\w+)\s*=\s*\1\s*;', r'\1=mastery_alias(\1);', snippets)
            snippets = re.sub(r'\b(\w+)\s*=\s*std::move\(\1\);', r'\1=std::move(mastery_alias(\1));', snippets)
            dispatch = '\n'.join(f'case {i}: test_{i}(); break;' for i in range(len(task['tests'])))
            # Include student code FIRST: missing required headers must be detected.
            header = '#include "candidate.hpp"\n' + PREAMBLE
            harness = header + task.get('checks','') + '\n' + snippets + '''
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    try {
        const auto live_before = mastery_memory::live;
        switch (std::stoi(argv[1])) {
''' + dispatch + '''
        default: return 2;
        }
        mastery_memory::fail_after=-1;
        CHECK(mastery_memory::live==live_before);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what(); return 1;
    } catch (...) { std::cerr << "unexpected non-standard exception"; return 1; }
}
'''
            (tests_dir / f"{task['id']}.cpp").write_text(harness, encoding='utf-8')
        student_files(task)
    for i,name in enumerate(DAY_NAMES,1):
        if day01_v2 and i==1: continue
        day = ROOT/'days'/f'day-{i:02}-{name}'
        tasks = [t for t in TASKS if t['day']==i]
        counts = ', '.join(f'{k}: {sum(t["kind"]==k for t in tasks)}' for k in ('Q','S','P','D','C'))
        rows = '\n'.join(f'| {t["id"]} | {t["kind"]} / {t["level"]} | {t["title"]} | {t["minutes"]} мин |' for t in tasks)
        (day/'README.md').write_text(f'# День {i}. {TITLES[i-1]}\n\n4–6 часов основной работы; сложные задачи могут потребовать продолжения.\n\n{counts}\n\nТемы: '+', '.join(TOPICS[i-1])+f'\n\nВсе задания обязательны, кроме явно обозначенного расширения. Незакрытые задания остаются долгами.\n\n| ID | Блок / уровень | Задание | Ориентир |\n|---|---|---|---|\n{rows}\n',encoding='utf-8')
    metadata = [dict(id=i+1, title=t, subtitle=['Классы, арифметика и потоки', 'Владение ресурсом и безопасность', 'От вывода типа к специализации', 'Архитектура, полиморфизм и типы', 'Собственный контейнер TSequence<T>'][i], topics=TOPICS[i], duration='4–6 часов') for i,t in enumerate(TITLES)]
    (ROOT/'days'/'course.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    from backend.catalog import catalog
    print(f'Course ready: {len(catalog())} active exercises. Existing student files preserved.')

if __name__ == '__main__': generate()
