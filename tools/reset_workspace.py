"""Reset learner data only. Run with --apply after stopping the local server."""
import argparse
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import DATA

STUDENT_FILES={'solution.hpp','solution.cpp','main.cpp','notes.md','answer.json','test_adapter.hpp','migration.json','Matrix2x2.hpp','Matrix2x2.cpp','Point2D.hpp','CMyString.hpp','CMyString.h','CMyString.cpp','DynamicVector.hpp','DynamicVector.h','DynamicVector.cpp','GenericAlgorithms.h','FixedStack.h','IStack.h','LinkedStack.h','PostfixEvaluator.h','RttiLab.h','forward_chain.hpp','bidirectional_list.hpp','collection_operations.hpp'}

def reset_workspace(root,*,apply=False,clear_cache=False):
    root=Path(root).resolve()
    areas=['student','progress']+(['.build','test-results'] if clear_cache else [])
    files=[];directories=[]
    for area in areas:
        base=root/area
        if not base.exists():continue
        if base.is_symlink() or base.resolve()!=base:raise ValueError('Refusing a linked data directory')
        for path in base.rglob('*'):
            if path.is_symlink() or not path.resolve().is_relative_to(base):raise ValueError('Data path escapes its intended directory')
            if path.is_dir():directories.append(path);continue
            if area=='student' and path==base/'README.md':continue
            if area=='progress' and path==base/'.gitkeep':continue
            python_source=area=='student' and len(path.relative_to(base).parts)==3 and path.relative_to(base).parts[0]=='python' and re.fullmatch(r'py-(?:0[1-9]|[1-3][0-9]|40)',path.parent.name) and re.fullmatch(r'(?:day_(?:0[1-9]|[1-3][0-9]|40)|main|utils)\.py',path.name)
            if area=='student' and path.name not in STUDENT_FILES and path.name!='.gitkeep' and not python_source:raise ValueError('Unexpected learner file: '+str(path.relative_to(root)))
            if area=='progress' and not re.fullmatch(r'.+\.sqlite3(?:-wal|-shm)?|workspace-id',path.name):raise ValueError('Unexpected progress file: '+str(path.relative_to(root)))
            files.append(path)
    # All paths and filenames are checked before removing any file. No recursive
    # delete or shell interpolation is used; unrelated files stop the reset.
    if apply:
        for path in files:path.unlink()
        for path in sorted(directories,key=lambda p:len(p.parts),reverse=True):path.rmdir()
    return {'files':len(files),'directories':len(directories),'applied':apply}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true');parser.add_argument('--clear-cache',action='store_true')
    args=parser.parse_args()
    print(reset_workspace(DATA,apply=args.apply,clear_cache=args.clear_cache))

if __name__=='__main__':main()
