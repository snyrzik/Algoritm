import io
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend.catalog import ROOT,catalog,get_task,student_files
from backend.self_check import guide,report,bundle
from backend import storage

class SelfCheckContentTests(unittest.TestCase):
    def test_all_programming_tasks_have_main_cases_and_expected_output(self):
        tasks=[t for t in catalog(True) if t['kind'] in ('S','D','C')];self.assertEqual(len(tasks),21)
        for task in tasks:
            if task.get('localAssessment'):continue
            current=guide(task);self.assertIn('int main()',current['main'],task['id']);self.assertTrue(current['cases'])
            self.assertEqual(len(current['cases']),len({c['id'] for c in current['cases']}))
            self.assertNotIn('\x00',current['main'],task['id'])
            self.assertTrue(current['expectedOutput'])
            if not current.get('assertBased'):self.assertIn('ALL CHECKS PASSED',current['expectedOutput'])
    def test_retired_questions_are_absent(self):
        for key in ['d4-q01','d4-p01','d5-q01']:
            self.assertIsNone(get_task(key))
    def test_local_bundle_preserves_user_work(self):
        task=get_task('l01-v3-p01');files=student_files(task)
        with zipfile.ZipFile(io.BytesIO(bundle(task))) as archive:
            for name,source in files.items():
                if name.endswith(('.hpp','.cpp')):self.assertEqual(archive.read(name).decode(),source)
            self.assertIn('Point2D.hpp',archive.namelist())
        self.assertEqual(student_files(task),files)
    def test_explicit_confirmation_is_reversible_and_not_automatic_pass(self):
        task=get_task('l01-v3-p01');files=student_files(task);current=guide(task)
        with self.assertRaises(ValueError):report(task,{'completed':True,'checkedCases':[]},files)
        result=report(task,{'completed':True,'checkedCases':[c['id'] for c in current['cases']]},files)
        self.assertEqual(result['status'],'SELF_CHECKED');self.assertTrue(result['manual']);self.assertNotIn('compiled',result)
        self.assertEqual(report(task,{'completed':False},files)['status'],'NEEDS_WORK')
    def test_runtime_imports_no_compiler(self):
        code='import backend.server,sys;assert "backend.compiler" not in sys.modules;assert "backend.grading" not in sys.modules;assert "tools.cpp_toolchain" not in sys.modules'
        value=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(value.returncode,0,value.stderr)

class SelfCheckApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request
    def test_opening_main_does_not_record_completion(self):
        key='l01-v3-p03';before=len(storage.history(key));status,current=self.request('/api/self-check/'+key)
        self.assertEqual(status,200);self.assertEqual(len(storage.history(key)),before)
        _,value=self.request('/api/self-check/'+key,{'completed':True,'checkedCases':[c['id'] for c in current['cases']]})
        self.assertEqual(value['status'],'SELF_CHECKED')
        _,detail=self.request('/api/task/'+key);self.assertEqual(detail['history'][0]['status'],'SELF_CHECKED')
        self.request('/api/self-check/'+key,{'completed':False})
    def test_retired_compilation_and_input_validation(self):
        self.assertEqual(self.request('/api/doctor')[0],410)
        self.assertEqual(self.request('/api/run/l01-v3-p01',{'mode':'test'})[0],410)
        self.assertEqual(self.request('/api/self-check/l01-v3-p01',{'completed':True},token=False)[0],403)
        self.assertEqual(self.request('/api/self-check/l01-v3-p01',{'completed':True,'checkedCases':['fake']})[0],400)

if __name__=='__main__':unittest.main()
