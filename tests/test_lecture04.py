"""Lecture four source fidelity, thoughtful local practice, and independent progress."""
import hashlib
import io
import json
import sys
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend.catalog import ROOT,get_task,student_files
from backend.lectures import lecture,guide,reading,bundle
from backend import storage

SOURCE=ROOT/'content/lecture-04'

class LectureFourContentTests(unittest.TestCase):
    def test_all_seven_original_files_and_complete_theory_are_preserved(self):
        hashes=json.loads((SOURCE/'source.sha256.json').read_text(encoding='utf-8'))
        self.assertEqual(len(hashes),7)
        for name,digest in hashes.items():self.assertEqual(hashlib.sha256((SOURCE/name).read_bytes()).hexdigest(),digest,name)
        data=lecture(4)
        self.assertEqual(''.join(s['markdown'] for s in data['sections']).encode(),(SOURCE/'lecture-04/LECTURE_04_THEORY.md').read_bytes())
        self.assertEqual([s['chapter'] for s in data['sections'] if 'chapter' in s],[1,2,3,4])
        self.assertEqual(len(data['checks']),4);self.assertEqual(len(data['projects']),3)
        for task in data['checks']:
            self.assertIn(task['prompt'].split('\n\n## Самостоятельная попытка')[0],''.join(s['markdown'] for s in data['sections']))
            self.assertFalse(task['localMains'])
        self.assertIn('ортогональ',data['sections'][2]['markdown'])
        self.assertIn('амортиз',data['sections'][4]['markdown'])

    def test_prior_materials_and_navigation_entries_are_identical(self):
        # Stable hashes also work in a source export or a shallow Git checkout.
        for name,count,digest in (
            ('days/course.json',3,'362ab945a6ce6b78c77742e70023cf0697325b194c1b26a8e239c39f8d6f6c6b'),
            ('app/src/lectures/catalog.json',2,'f1aee431b9807b3f89b49d385c25d531b2782236c3a6341427b72729abd72601')):
            after=json.loads((ROOT/name).read_text(encoding='utf-8'))
            self.assertEqual(hashlib.sha256(json.dumps(after[:count],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),digest)

    def test_projects_have_only_empty_starters_and_exact_author_contracts(self):
        instructions=(SOURCE/'lecture-04/CODEX_INSTRUCTIONS.md').read_text(encoding='utf-8')
        for task in lecture(4)['projects']:
            self.assertTrue(task['requiresComplexity']);self.assertTrue(task['trackImplementation'])
            self.assertGreaterEqual(len(task['projectSteps']),5)
            self.assertEqual(len(task['localMains']),1)
            self.assertIn(task['prompt'].split('\n\n### Самостоятельная реализация')[0],instructions)
            for text in task['starterFiles'].values():self.assertTrue(all(not line or line.startswith('//') for line in text.splitlines()))
        self.assertIsNone(get_task('d4-c01'));self.assertIsNone(get_task('d5-c01'))

class LectureFourApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request

    def test_reading_bookmarks_and_resume_are_separate_from_earlier_lectures(self):
        previous={n:reading(n) for n in (2,3)};attempts=storage.history()
        status,value=self.request('/api/lecture-reading/4',{'section':'chapter-2','completed':True})
        self.assertEqual(status,200);self.assertIn('chapter-2',value['reading'])
        self.assertEqual(previous,{n:reading(n) for n in (2,3)});self.assertEqual(storage.history(),attempts)
        self.assertEqual(self.request('/api/lecture-reading/4',{'section':'chapter-5','completed':True})[0],400)
        status,value=self.request('/api/learning',{'lastPath':'theory/4/chapter-2','bookmarks':['l04-local-p01']})
        self.assertEqual(status,200);self.assertEqual(value['lastPath'],'theory/4/chapter-2')
        self.assertEqual(self.request('/api/learning',{'lastPath':'theory/5/chapter-1'})[0],400)

    def test_partial_implementation_and_notes_save_without_completing_project(self):
        key='l04-local-p01';task=get_task(key);stage=guide(task)['stages'][0]['id']
        body=dict(stage=stage,status='IN_PROGRESS',implementation=[0,1],compileNotes='Local compiler diagnostic',reviewNotes='Recheck head ownership',complexityNotes='My partial explanation',hints='Chapter 1',memory='not_checked')
        status,value=self.request('/api/lecture-state/'+key,body)
        self.assertEqual(status,200);self.assertEqual(value['status'],'IN_PROGRESS')
        _,loaded=self.request('/api/lecture-task/'+key);self.assertEqual(loaded['reports'][stage]['implementation'],[0,1])
        self.assertEqual(loaded['reports'][stage]['compileNotes'],'Local compiler diagnostic')
        self.assertEqual(loaded['reports'][stage]['reviewNotes'],'Recheck head ownership')
        self.assertNotIn('compiled',value)
        body.update(status='SELF_CHECKED',confirmed=list(range(len(task['reviewRequirements']))))
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[0],400)
        body['implementation']=list(range(len(task['projectSteps'])));body['complexityNotes']=''
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[0],400)
        body['complexityNotes']='My explanation of traversal and constant pointer changes.';body['memory']='errors'
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[0],400)
        body['memory']='sanitized';status,value=self.request('/api/lecture-state/'+key,body)
        self.assertEqual(status,200);self.assertEqual(value['status'],'SELF_CHECKED')
        self.assertEqual(value['stageReports'][stage]['memory'],'sanitized')
        self.assertFalse(storage.history('l04-local-p02'))
        self.assertEqual(self.request('/api/lecture-state/'+key,{**body,'implementation':[999]})[0],400)

    def test_checkpoint_requires_explanation_and_keeps_attempts(self):
        key='l04-local-c04';task=get_task(key)
        body=dict(stage='reflection',status='SELF_CHECKED',confirmed=list(range(len(task['reviewRequirements']))))
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[0],400)
        body['explanation']='I counted the work of every loop and the full push_back series.'
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[1]['status'],'SELF_CHECKED')
        self.assertEqual(self.request('/api/lecture-state/'+key,{**body,'status':'REPEAT_REQUESTED'})[1]['status'],'REPEAT_REQUESTED')
        self.assertEqual(storage.history(key)[1]['status'],'SELF_CHECKED')

    def test_mains_and_bundles_preserve_source_and_learner_code(self):
        import http.client
        for task in lecture(4)['projects']:
            main=task['localMains'][0];client=http.client.HTTPConnection('127.0.0.1',self.port)
            client.request('GET','/api/lecture-main/4/'+main['filename']);response=client.getresponse()
            self.assertEqual(response.status,200);original=(SOURCE/main['sourcePath']).read_bytes()
            self.assertEqual(response.read(),original);client.close()
            files=student_files(task);folder=platform.DATA/'student/day-04'/task['id'];header=next(iter(task['starterFiles']))
            (folder/header).write_text('// My own implementation draft',encoding='utf-8')
            before=(folder/header).read_bytes()
            with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
                self.assertEqual(archive.read(main['filename']),original)
                self.assertEqual(archive.read(header),before)
                self.assertIn('README.md',archive.namelist())
            self.assertEqual((folder/header).read_bytes(),before)

if __name__=='__main__':unittest.main()
