import http.client
import io
import json
import subprocess
import sys
import threading
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend.catalog import ROOT,catalog,get_task,student_files
from backend.self_check import guide,report,bundle
from backend import storage
from backend.day01_v2.scoring import summary

class SelfCheckContentTests(unittest.TestCase):
    def test_every_programming_exercise_has_main_edges_and_expected_result(self):
        tasks=[t for t in catalog(include_theory=True) if t['kind'] in ('S','D','C')]
        self.assertEqual(len(tasks),171)
        for task in tasks:
            current=guide(task);self.assertIn('int main()',current['main'],task['id']);self.assertTrue(current['cases'])
            self.assertEqual(len(current['cases']),len({c['id'] for c in current['cases']}))
            self.assertNotIn('#include "support.hpp"',current['main'])
            if not current['console']:
                self.assertIn(f'ALL CHECKS PASSED ({len(current["cases"])})',current['expectedOutput'])
                for case in current['cases']:self.assertIn(case['id']+': OK',current['expectedOutput'])
            else:
                self.assertEqual(len(current['cases']),13)
                self.assertTrue(any(c['exitCode']!=0 and c['expectedOutput']=='' for c in current['cases']))
    def test_question_answers_are_not_exposed_by_main_endpoint(self):
        for name in ('d01-v2-q01','d01-v2-p01'):
            with self.assertRaises(ValueError):guide(get_task(name))
    def test_short_exercises_do_not_include_memory_instrumentation(self):
        self.assertNotIn('void* operator new',guide(get_task('d01-v2-s01'))['main'])
        self.assertIn('void* operator new',guide(get_task('d01-v2-a03'))['main'])
    def test_download_contains_self_contained_helpers_and_student_files(self):
        task=get_task('d01-v2-a02');expected=student_files(task)['solution.hpp']
        with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
            self.assertEqual(archive.read('solution.hpp').decode(),expected)
            self.assertIn('StereoSample.hpp',archive.namelist())
            self.assertIn('expected.txt',archive.namelist())
            self.assertNotIn('operator+=',archive.read('StereoSample.hpp').decode())
        task=get_task('d01-v2-b02')
        with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
            self.assertIn('dependencies/d01-v2-a03/solution.hpp',archive.namelist())
            self.assertIn('AudioBlock.hpp',archive.namelist())
            sources=[Path(name).name for name in archive.namelist() if name.endswith('.cpp')]
            self.assertEqual(len(sources),len(set(sources)))
    def test_debugging_keeps_original_defect_and_syntax_keeps_context(self):
        task=get_task('d01-v2-d02');self.assertEqual(guide(task)['originalCode'],task['starter'])
        self.assertIn('class Score',get_task('d01-v2-s04')['prefix'])
    def test_self_confirmation_is_explicit_reversible_and_not_an_automatic_pass(self):
        task=get_task('d01-v2-s01');files=student_files(task);current=guide(task)
        with self.assertRaises(ValueError):report(task,{'completed':True,'checkedCases':[]},files)
        result=report(task,{'completed':True,'checkedCases':[c['id'] for c in current['cases']]},files)
        self.assertEqual(result['status'],'SELF_CHECKED');self.assertTrue(result['manual']);self.assertNotIn('compiled',result)
        self.assertEqual(result['pointsEarned'],2)
        result=report(task,{'completed':False},files);self.assertEqual(result['status'],'NEEDS_WORK');self.assertEqual(result['pointsEarned'],0)
    def test_server_import_does_not_load_a_compiler(self):
        code='import backend.server,sys;assert "backend.compiler" not in sys.modules;assert "backend.grading" not in sys.modules'
        result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

class SelfCheckApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request
    def test_loading_main_does_not_complete_task_and_mark_survives_reload(self):
        task_id='d01-v2-a01'
        before=len(storage.history(task_id));status,current=self.request('/api/self-check/'+task_id)
        self.assertEqual(status,200);self.assertEqual(len(storage.history(task_id)),before)
        status,result=self.request('/api/self-check/'+task_id,{'completed':True,'checkedCases':[c['id'] for c in current['cases']]})
        self.assertEqual(status,200);self.assertEqual(result['status'],'SELF_CHECKED')
        _,loaded=self.request('/api/task/'+task_id);self.assertEqual(loaded['history'][0]['status'],'SELF_CHECKED')
        self.assertGreaterEqual(summary()['earned'],10)
        self.request('/api/self-check/'+task_id,{'completed':False})
        self.assertEqual(storage.history(task_id)[0]['status'],'NEEDS_WORK')
    def test_compiler_routes_are_retired_and_require_no_environment(self):
        self.assertEqual(self.request('/api/doctor')[0],410)
        status,data=self.request('/api/run/d01-v2-s02',{'mode':'test'});self.assertEqual(status,410)
    def test_authentication_and_validation_apply_to_manual_completion(self):
        self.assertEqual(self.request('/api/self-check/d01-v2-s03',{'completed':True},token=False)[0],403)
        self.assertEqual(self.request('/api/self-check/d01-v2-s03',{'completed':True,'checkedCases':['fake']})[0],400)
        self.assertEqual(self.request('/api/self-check/d01-v2-q01',{'completed':True})[0],400)

if __name__=='__main__':unittest.main()
