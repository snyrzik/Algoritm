"""Day 1 / lecture 1 only. The supplied Markdown is kept byte for byte."""
import hashlib
import json
import re
from .catalog import ROOT, get_task, public_task

LECTURE = ROOT / 'days' / 'day-01-operators' / 'theory' / 'lecture-01'
CHECK_IDS = [f'd1-l1-c{i:02}' for i in range(1, 5)]

def lecture():
    content = (LECTURE / 'theory.md').read_bytes()
    markdown = content.decode('utf-8')
    boundaries = list(re.finditer(r'^# (Глава [1-4]\..+|Итоги теории Дня 1)\r?$', markdown, re.M))
    if len(boundaries) != 5:
        raise ValueError('В лекции должны быть четыре главы и раздел итогов')
    sections = [dict(id='overview', title='О лекции', markdown=markdown[:boundaries[0].start()])]
    for i, match in enumerate(boundaries):
        end = boundaries[i+1].start() if i+1 < len(boundaries) else len(markdown)
        item = dict(id=f'chapter-{i+1}' if i<4 else 'summary', title=match[1], markdown=markdown[match.start():end])
        if i<4:
            item['chapter'] = i+1
            item['checkId'] = CHECK_IDS[i]
        sections.append(item)
    return {'id':'day-1-lecture-1', 'day':1, 'lecture':1, 'title':'Классы и перегрузка операций в C++17', 'sourceFilename':'CppMastery_Day01_Theory_READY.md', 'sourceSha256':hashlib.sha256(content).hexdigest(), 'sections':sections, 'checks':[public_task(get_task(task_id)) for task_id in CHECK_IDS]}
