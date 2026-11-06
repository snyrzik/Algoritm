"""Source fidelity, local main downloads, stage progress, and preservation of earlier work."""
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
from backend import storage
from backend.catalog import ROOT,catalog,get_task,student_files
from backend.lectures import SOURCE,lecture,guide
from backend.theory import reading as first_reading
from backend.saved_work import records

class PackContentTests(unittest.TestCase):
    def test_all_fourteen_pack_files_are_byte_identical(self):
        source=json.loads((SOURCE/'source.sha256.json').read_text(encoding='utf-8'));self.assertEqual(len(source),14)
        for name,digest in source.items():self.assertEqual(hashlib.sha256((SOURCE/name).read_bytes()).hexdigest(),digest,name)
    def test_each_theory_is_complete_with_four_chapters_and_four_checks(self):
        for number in (2,3):
            data=lecture(number)
            self.assertEqual(''.join(section['markdown'] for section in data['sections']).encode(),(SOURCE/f'lecture-{number:02}'/data['sourceFilename']).read_bytes())
            self.assertEqual([s['chapter'] for s in data['sections'] if 'chapter' in s],[1,2,3,4])
            self.assertEqual(len(data['checks']),4);self.assertEqual(len(data['projects']),2 if number==2 else 3)
            for task in data['checks']:self.assertIn(task['prompt'].split('\n\n## RTTI')[0],''.join(s['markdown'] for s in data['sections']))
        self.assertIn('переходный',lecture(2)['title']);self.assertIn('недоступен',lecture(2)['attribution'])
    def test_no_starters_contain_finished_implementations(self):
        for task in catalog(True):
            if not task.get('packLecture') or task['section']!='lecture-practice':continue
            for name,source in task['starterFiles'].items():
                self.assertNotIn('class ',source);self.assertNotIn('return ',source)
    def test_continuations_copy_only_learner_code_and_never_overwrite_either_version(self):
        with tempfile.TemporaryDirectory() as temp,patch('backend.catalog.DATA',Path(temp)):
            base=get_task('l01-v3-p02');new=get_task('l02-local-p01')
            folder=Path(temp)/'student/day-01'/base['id'];folder.mkdir(parents=True)
            (folder/'CMyString.hpp').write_text('// my existing source',encoding='utf-8')
            self.assertEqual(student_files(new)['CMyString.hpp'],'// my existing source')
            target=Path(temp)/'student/day-02'/new['id']/'CMyString.hpp';target.write_text('// my extension',encoding='utf-8')
            self.assertEqual(student_files(new)['CMyString.hpp'],'// my extension')
            self.assertEqual((folder/'CMyString.hpp').read_text(encoding='utf-8'),'// my existing source')
    def test_retired_metadata_keeps_only_identity_and_not_old_assignments(self):
        self.assertGreaterEqual(len(records()),240)
        for item in records():
            self.assertEqual(set(item),{'id','day','title','filePath'})
            self.assertIsNone(get_task(item['id']))

class PackApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request
    def get_bytes(self,path):
        client=http.client.HTTPConnection('127.0.0.1',self.port);client.request('GET',path);response=client.getresponse();value=response.read();status=response.status;client.close();return status,value
    def test_all_seven_main_downloads_match_original_files(self):
        count=0
        for number in (2,3):
            data=lecture(number)
            for task in data['checks']+data['projects']:
                for main in task['localMains']:
                    status,raw=self.get_bytes(f'/api/lecture-main/{number}/{main["filename"]}')
                    self.assertEqual(status,200);self.assertEqual(raw,(SOURCE/main['sourcePath']).read_bytes());count+=1
        self.assertEqual(count,7)
        self.assertEqual(self.get_bytes('/api/lecture-main/2/unknown.cpp')[0],400)
    def test_reading_is_separate_for_every_lecture(self):
        previous=first_reading()
        self.request('/api/lecture-reading/2',{'section':'chapter-1','completed':True})
        self.assertEqual(first_reading(),previous)
        _,progress=self.request('/api/progress');self.assertIn('lecture-2/chapter-1',progress['reading'])
        self.request('/api/lecture-reading/2',{'section':'chapter-1','completed':False})
    def test_postfix_is_an_independent_stage_of_project_three(self):
        key='l03-local-p03';current=guide(get_task(key));stages=current['stages'];self.assertEqual(len(stages),2)
        confirmed=list(range(len(current['requirements'])))
        _,first=self.request('/api/lecture-state/'+key,{'stage':stages[0]['id'],'status':'SELF_CHECKED','confirmed':confirmed,'memory':'reviewed'})
        self.assertEqual(first['status'],'IN_PROGRESS');self.assertNotIn('compiled',first)
        _,second=self.request('/api/lecture-state/'+key,{'stage':stages[1]['id'],'status':'SELF_CHECKED','confirmed':confirmed})
        self.assertEqual(second['status'],'SELF_CHECKED')
        _,repeat=self.request('/api/lecture-state/'+key,{'stage':stages[1]['id'],'status':'REPEAT_REQUESTED','errorNotes':'Repeat signed tokens'})
        self.assertEqual(repeat['status'],'REPEAT_REQUESTED');self.assertEqual(repeat['stageReports'][stages[0]['id']]['status'],'SELF_CHECKED')
    def test_reflection_and_criteria_are_required_and_never_automatically_marked(self):
        key='l02-local-c03';before=len(storage.history(key));_,current=self.request('/api/lecture-task/'+key);self.assertEqual(len(storage.history(key)),before)
        body={'stage':'reflection','status':'SELF_CHECKED','confirmed':list(range(len(current['requirements'])))}
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[0],400)
        body['explanation']='My explanation of both failure cases.'
        self.assertEqual(self.request('/api/lecture-state/'+key,body)[1]['status'],'SELF_CHECKED')
        self.assertEqual(self.request('/api/lecture-state/'+key,{**body,'memory':'errors'})[0],400)
        self.assertEqual(self.request('/api/lecture-state/'+key,body,token=False)[0],403)
    def test_removed_work_remains_downloadable_without_retired_teaching_text(self):
        key=records()[0]['id'];storage.record(key,'self-check',{'status':'SELF_CHECKED','score':100},{'notes.md':'My old explanation'})
        _,items=self.request('/api/saved-work');self.assertTrue(any(item['id']==key and item['attempts'] for item in items))
        status,payload=self.get_bytes('/api/saved-work-bundle');self.assertEqual(status,200)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            rows=json.loads(archive.read('results.json'));self.assertTrue(any(item['task']==key for item in rows));self.assertNotIn('exercise.json',archive.namelist())
        self.assertEqual(self.request('/api/task/'+key)[0],404)

if __name__=='__main__':unittest.main()
