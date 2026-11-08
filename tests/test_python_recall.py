"""Independent subject, honest attempt gating, privacy, and text-only local work."""
import hashlib
import http.client
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend import python_recall as py,storage
from backend.catalog import ROOT,DATA

class PythonContentTests(unittest.TestCase):
    def test_complete_public_pack_and_starters_match_original_hashes(self):
        manifest=json.loads((py.SOURCE/'source.sha256.json').read_text(encoding='utf-8'))
        for name,entry in manifest.items():
            if entry['private']:continue
            self.assertEqual(hashlib.sha256((py.SOURCE/name).read_bytes()).hexdigest(),entry['sha256'],name)
        data=py.catalog();self.assertEqual(len(data['weeks']),8);self.assertEqual(len(data['tasks']),40)
        self.assertEqual({t['id'] for t in data['tasks']},{f'py-{n:02}' for n in range(1,41)})
        for week in range(1,9):self.assertEqual([t['day'] for t in data['tasks'] if t['week']==week],[1,2,3,4,5])
        for task in data['tasks']:
            for name,text in task['starter_files'].items():
                source=py.SOURCE/('starters/day_14/'+name if task['id']=='py-14' else task['starter_file'])
                self.assertEqual(source.read_text(encoding='utf-8'),text)
            self.assertTrue((py.SOURCE/task['task_md_file']).is_file())
        self.assertEqual(set(py.task('py-14')['starter_files']),{'main.py','utils.py'})
        self.assertTrue(all(py.task(f'py-{n:02}')['optional_topic'] for n in [21,22,23,25,26,27,28,29,31,32,33,34,36,37]))

    def test_solutions_are_not_in_public_sources_or_build(self):
        self.assertFalse((py.SOURCE/'solutions').exists());self.assertFalse((py.SOURCE/'import/private_solutions.json').exists())
        for asset in (ROOT/'app/dist').rglob('*'):
            if asset.suffix in ('.js','.json','.html'):self.assertNotIn('private_solutions',asset.read_text(encoding='utf-8'))

class PythonApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request

    def test_public_endpoints_never_include_answers_and_cpp_catalog_is_unchanged(self):
        before=storage.history();_,course=self.request('/api/python/course')
        self.assertEqual(len(course['tasks']),40);self.assertEqual(len(course['weeks']),8)
        for task in course['tasks']:
            self.assertFalse({'solution_files','explanation','hint','manual_review'}&task.keys())
        _,cpp=self.request('/api/course');self.assertEqual(len(cpp['tasks']),28)
        self.assertEqual(storage.history(),before)

    def test_hint_and_unchanged_or_comment_only_drafts_do_not_unlock_answer(self):
        key='py-02';self.assertEqual(self.request('/api/python/solution/'+key)[0],403)
        self.assertEqual(self.request('/api/python/hint/'+key)[0],200)
        _,detail=self.request('/api/python/task/'+key)
        sources={name:text+'\n# own comment only\n' for name,text in detail['files'].items()}
        self.assertEqual(self.request('/api/python/files/'+key,{'files':sources,'revision':detail['revision']},method='PUT')[0],200)
        _,result=self.request('/api/python/state/'+key,{'status':'in_progress'})
        self.assertFalse(result['solutionUnlocked']);self.assertEqual(self.request('/api/python/solution/'+key)[0],403)

    def test_saved_attempt_unlocks_only_its_answer_and_never_executes_python(self):
        key='py-01';_,detail=self.request('/api/python/task/'+key);sources=detail['files'];name=next(iter(sources))
        marker=DATA/'executed.txt';sources[name]=f'from pathlib import Path\nPath({str(marker)!r}).write_text("executed")\n'
        self.request('/api/python/files/'+key,{'files':sources,'revision':detail['revision']},method='PUT')
        self.assertEqual(self.request('/api/python/solution/'+key)[0],403)
        before=storage.history();status,value=self.request('/api/python/state/'+key,{'status':'in_progress','notes':'A syntax attempt to discuss','weakTopics':['imports']})
        self.assertEqual(status,200);self.assertTrue(value['solutionUnlocked']);self.assertFalse(marker.exists());self.assertEqual(storage.history(),before)
        with tempfile.TemporaryDirectory() as temp:
            private=Path(temp)/'private.json';private.write_text(json.dumps({'tasks':[{'id':key,'solution_files':{'reference.py':'PRIVATE_REFERENCE_SENTINEL'},'explanation':'Private explanation','test_reference':'never return'}]}),encoding='utf-8')
            with patch.object(py,'PRIVATE',private):
                status,answer=self.request('/api/python/solution/'+key);self.assertEqual(status,200);self.assertIn('PRIVATE_REFERENCE_SENTINEL',json.dumps(answer));self.assertNotIn('test_reference',answer)
                self.assertEqual(self.request('/api/python/solution/py-03')[0],403)
        _,after=self.request('/api/python/task/'+key);self.assertTrue(after['solutionUnlocked']);self.assertEqual(after['state']['status'],'in_progress');self.assertNotIn('solution_files',after)

    def test_external_work_needs_explanation_and_completion_is_explicit(self):
        key='py-04'
        self.assertEqual(self.request('/api/python/state/'+key,{'status':'completed','localChecked':True})[0],400)
        _,value=self.request('/api/python/state/'+key,{'status':'in_progress','external':True,'notes':'Too short'})
        self.assertFalse(value['solutionUnlocked'])
        status,value=self.request('/api/python/state/'+key,{'status':'completed','external':True,'notes':'I implemented the calculation locally and checked invalid input.','localChecked':True,'difficulty':'hard','weakTopics':['exceptions']})
        self.assertEqual(status,200);self.assertTrue(value['solutionUnlocked']);self.assertEqual(value['state']['status'],'completed')
        self.request('/api/python/state/'+key,{'status':'revisit'})
        _,detail=self.request('/api/python/task/'+key);self.assertEqual(detail['state']['status'],'revisit');self.assertGreaterEqual(len(detail['history']),2)

    def test_two_file_saving_conflict_protection_and_own_bundle(self):
        key='py-14';_,detail=self.request('/api/python/task/'+key);self.assertEqual(set(detail['files']),{'main.py','utils.py'})
        path=DATA/'student/python'/key/'main.py';path.write_text('# external edit',encoding='utf-8')
        self.assertEqual(self.request('/api/python/files/'+key,{'files':detail['files'],'revision':detail['revision']},method='PUT')[0],409)
        _,detail=self.request('/api/python/task/'+key);sources={**detail['files'],'../escape.py':'no'}
        self.assertEqual(self.request('/api/python/files/'+key,{'files':sources,'revision':detail['revision']},method='PUT')[0],400)
        client=http.client.HTTPConnection('127.0.0.1',self.port);client.request('GET','/api/python/bundle/'+key);response=client.getresponse();self.assertEqual(response.status,200)
        with zipfile.ZipFile(io.BytesIO(response.read())) as archive:
            self.assertEqual(archive.read('main.py'),b'# external edit');self.assertEqual(set(archive.namelist()),{'main.py','utils.py','task.md','LOCAL_RUN.md'})
        client.close()

    def test_preferences_skips_and_python_learning_do_not_change_cpp_state(self):
        _,before=self.request('/api/learning');before_history=storage.history()
        self.request('/api/python/state/py-31',{'skipped':True,'topicReady':False,'bookmark':True})
        self.request('/api/python/learning',{'lastPath':'python/task/py-31'})
        _,progress=self.request('/api/python/progress');self.assertTrue(progress['states']['py-31']['skipped']);self.assertEqual(progress['lastPath'],'python/task/py-31')
        _,after=self.request('/api/learning');self.assertEqual(before,after);self.assertEqual(storage.history(),before_history)
        self.assertEqual(self.request('/api/python/learning',{'lastPath':'task/l01-v3-p01'})[0],400)
        self.assertEqual(self.request('/api/python/state/py-31',{'bookmark':False},token=False)[0],403)
        self.assertEqual(self.request('/api/python/state/py-31',{'bookmark':False},origin='http://evil.example')[0],403)

if __name__=='__main__':unittest.main()
