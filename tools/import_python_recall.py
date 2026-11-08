"""Import supplied Python Recall content. Answers stay in ignored server-only storage."""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.catalog import ROOT

def import_pack(filename):
    checksums={}
    with zipfile.ZipFile(filename) as archive:
        public=json.loads(archive.read('python_recall_8_weeks/import/public_catalog.json'))
        private=json.loads(archive.read('python_recall_8_weeks/import/private_solutions.json'))
        if {t['id'] for t in public['tasks']}!={f'py-{n:02}' for n in range(1,41)} or len(public['tasks'])!=40 or len(public['weeks'])!=8:raise ValueError('Expected eight weeks and forty unique tasks')
        if {t['id'] for t in private['tasks']}!={t['id'] for t in public['tasks']}:raise ValueError('Private answers do not match tasks')
        for name in archive.namelist():
            if name.endswith('/'):continue
            relative=Path(name).relative_to('python_recall_8_weeks')
            if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe archive path')
            hidden=relative.parts[0] in ('solutions','explanations','tests') or relative.as_posix()=='import/private_solutions.json'
            base=ROOT/('.private/python-recall' if hidden else 'content/python-recall')
            target=base/relative;target.parent.mkdir(parents=True,exist_ok=True)
            raw=archive.read(name);target.write_bytes(raw)
            checksums[relative.as_posix()]=dict(sha256=hashlib.sha256(raw).hexdigest(),private=hidden)
    (ROOT/'content/python-recall/source.sha256.json').write_text(json.dumps(checksums,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Imported eight weeks and forty tasks. Private reference solutions are outside public assets and Git. Learner files untouched.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive');args=parser.parse_args();import_pack(args.archive)
