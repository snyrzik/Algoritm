"""Replacement lecture fidelity, local checks, and isolation of the other days."""
import hashlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend.catalog import ROOT,catalog,get_task,student_files
from backend.theory import LECTURE,CHECK_IDS,PROJECT_IDS,lecture,summary
from backend.self_check import guide,bundle
from tools.replace_day01 import replace

SOURCE_SHA='b8940d0ddec865d8c518979ff3d818ca74efd82730c4fdcb5c0171cab4f3d982'
MAIN_HASHES=['0be46ce00937efea3a6c15f123babf78d2de5a9d812a1f7aa16800e36712b9a6','c8515a99ffb731e47cba5047282d4cfbfcdf31b68c22923df0322bfb91a17087','a3d173b89a1ed79f2eb08e73bdefcc0035d8f13b14d5ff72314b2b12accb8f6b']

class LectureContentTests(unittest.TestCase):
    def test_author_theory_is_complete_and_byte_identical(self):
        raw=(LECTURE/'theory.md').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA)
        value=lecture();self.assertEqual(''.join(s['markdown'] for s in value['sections']).encode(),raw)
        self.assertEqual([s['chapter'] for s in value['sections'] if 'chapter' in s],[1,2,3,4,5])
        for i,task_id in enumerate(CHECK_IDS,1):
            task=get_task(task_id);self.assertIn(task['prompt'],raw.decode());self.assertEqual(task['chapter'],i)
    def test_first_module_and_protected_sources_remain_unchanged(self):
        manifest=json.loads((ROOT/'tests/course_content.sha256.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest),1)
        for name,digest in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),digest,name)
        metadata=json.loads((ROOT/'days/course.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256(json.dumps(metadata[0],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'78a54cc3055f8ad0ce5941f68ae139c3cdc5b017a337849e530f136654b03aa6')
    def test_old_tasks_are_gone_and_new_projects_are_independent(self):
        self.assertEqual(len([t for t in catalog() if t['day']==1]),3);self.assertEqual(len([t for t in catalog(True) if t['day']==1]),8)
        self.assertEqual({t['id'] for t in catalog(True) if t['day']==1},set(CHECK_IDS+PROJECT_IDS))
        self.assertIsNone(get_task('d01-v2-a01'));self.assertIsNone(get_task('d1-l1-c04'))
        for task in lecture()['projects']:
            self.assertFalse(task.get('dependencies'));self.assertFalse({'tests','answer','hints','checks'}&task.keys())
    def test_supplied_mains_are_unchanged_and_bundles_have_real_filenames(self):
        for task_id,digest in zip(PROJECT_IDS,MAIN_HASHES):
            task=get_task(task_id);current=guide(task)
            self.assertEqual(hashlib.sha256(current['main'].encode()).hexdigest(),digest)
            files=student_files(task);self.assertIn(task['project']+'.hpp',files);self.assertNotIn('solution.hpp',files)
            with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
                self.assertEqual(archive.read('main.cpp').decode(),current['main'])
                self.assertEqual(archive.read(task['project']+'.hpp').decode(),files[task['project']+'.hpp'])
                self.assertEqual(archive.read('expected.txt').decode(),current['expectedOutput'])
                self.assertIn('README.md',archive.namelist())
    def test_replacement_deletes_only_old_day_one_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ['day-01/d01-v2-a01','day-01/d1-l1-c01','day-01/l01-v3-p01','day-02/d2-c01']:
                folder=root/'student'/name;folder.mkdir(parents=True);(folder/'solution.hpp').write_text(name)
            (root/'progress').mkdir()
            with closing(sqlite3.connect(root/'progress/mastery.sqlite3')) as db, db:
                db.execute('CREATE TABLE attempts(task TEXT)')
                db.executemany('INSERT INTO attempts VALUES(?)',[(x,) for x in ['d01-v2-a01','d1-l1-c01','l01-v3-p01','d2-c01']])
            replace(root)
            self.assertFalse((root/'student/day-01/d01-v2-a01').exists())
            self.assertTrue((root/'student/day-01/l01-v3-p01/solution.hpp').exists())
            self.assertTrue((root/'student/day-02/d2-c01/solution.hpp').exists())
            with closing(sqlite3.connect(root/'progress/mastery.sqlite3')) as db:self.assertEqual(db.execute('SELECT task FROM attempts').fetchall(),[('l01-v3-p01',),('d2-c01',)])

class LectureApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request
    def test_reading_is_explicit_reversible_and_separate_from_work(self):
        before=summary()['completed']
        _,value=self.request('/api/lecture-read/chapter-4',{'completed':True});self.assertIn('chapter-4',value['reading'])
        _,value=self.request('/api/theory/day-1/lecture-1');self.assertIn('chapter-4',value['reading'])
        self.assertEqual(summary()['completed'],before)
        _,value=self.request('/api/lecture-read/chapter-4',{'completed':False});self.assertNotIn('chapter-4',value['reading'])
        self.assertEqual(self.request('/api/lecture-read/chapter-6',{'completed':True})[0],400)
        self.assertEqual(self.request('/api/lecture-read/chapter-1',{'completed':True},token=False)[0],403)
    def test_check_progress_never_completes_a_project(self):
        before=summary()['projects'];key=CHECK_IDS[1];current=guide(get_task(key))
        _,value=self.request('/api/self-check/'+key,{'completed':True,'checkedCases':[c['id'] for c in current['cases']]})
        self.assertEqual(value['status'],'SELF_CHECKED');self.assertEqual(summary()['projects'],before)
        self.request('/api/self-check/'+key,{'completed':False})
    def test_old_routes_are_absent(self):
        for key in ['d01-v2-a01','d1-l1-c01']:
            self.assertEqual(self.request('/api/task/'+key)[0],404)
            self.assertEqual(self.request('/api/self-check/'+key)[0],404)

if __name__=='__main__':unittest.main()
