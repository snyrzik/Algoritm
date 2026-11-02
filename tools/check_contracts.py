"""Compile all practical harnesses against declarations, without student code."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT,DATA,catalog
from backend.compiler import toolchain,run_process

def main():
    tc=toolchain()
    if not tc['exe']: raise SystemExit('Compiler unavailable')
    folder=DATA/'.build'/'contract-audit';folder.mkdir(parents=True,exist_ok=True)
    (folder/'candidate.hpp').write_text('#include "contracts.hpp"\n',encoding='utf-8')
    failed=[]
    for task in catalog():
        if task['kind']!='C':continue
        if task.get('runner')=='console':
            from backend.day01_v2.console import cases
            assert len(cases())>=13
            print(task['id'],'console scenarios OK (compilation/runtime covered by tests/test_day01_v2.py)',flush=True)
            continue
        header='stereolab_contracts.hpp' if task.get('version')==2 else 'contracts.hpp'
        (folder/'candidate.hpp').write_text(f'#include "{header}"\n',encoding='utf-8')
        day=next(p for p in Path(task['_path']).parents if p.name.startswith('day-'))
        path=day/('practice-v2/tests' if task.get('version')==2 else 'tests')/f"{task['id']}.cpp"
        includes=[folder,ROOT/'tools',ROOT/'tests']
        args=[tc['exe'],'/nologo','/std:c++17','/EHsc','/W4','/WX','/utf-8','/Zs',*[f'/I{p}' for p in includes],path] if tc['kind']=='msvc' else [tc['exe'],'-std=c++17','-fsyntax-only',*[f'-I{p}' for p in includes],path]
        result=run_process(args,folder,tc['env'],30)
        if result['code']!=0:failed.append(task['id']);print(task['id'],result['output'],flush=True)
        else:print(task['id'],'contract OK',flush=True)
    print('Failed:',failed)
    return bool(failed)
if __name__=='__main__':raise SystemExit(main())
