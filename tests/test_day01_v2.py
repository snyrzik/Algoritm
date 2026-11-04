"""Exercise the real compiler and deliberate mutants in a disposable profile.

Reference code lives exclusively in tests/fixtures and must never reach student/.
"""
import http.client
import json
import os
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as legacy
from backend.catalog import ROOT,DATA,catalog,get_task,public_task,student_files,student_dir
from backend.compiler import doctor,run_process,compile_cpp,execute
from backend.grading import grade,grade_answer
from backend import storage
from backend.day01_v2.scoring import prediction,with_variant,diagnosis,summary
from backend.day01_v2.console import cases,evaluate
from day01_v2_helpers import reference_files,seeded_components,S_REFERENCES,debug_reference

TASKS=[t for t in catalog() if t.get('version')==2]

def code(source):return {'solution.hpp':source,'solution.cpp':'','notes.md':''}
def record_diagnosis(task):
    body={'explanation':'A causal analysis written for this isolated grader test.','rules':task['diagnosisAnswer']}
    return storage.record(task['id'],'diagnosis',diagnosis(task,body),body)

class StereoLabContentTests(unittest.TestCase):
    def test_identity_scoring_and_current_catalog(self):
        self.assertEqual(len(TASKS),48);self.assertEqual(sum(t['maxPoints'] for t in TASKS),130)
        self.assertEqual({g:sum(t['group']==g for t in TASKS) for g in 'QSP DABC'.replace(' ','')},dict(Q=16,S=14,P=6,D=6,A=3,B=2,C=1))
        self.assertTrue(all(t['id'].startswith('d01-v2-') for t in TASKS))
    def test_closed_material_never_enters_public_task(self):
        closed={'answer','expectedOutput','explanation','optionExplanations','variants','traceAnswer','diagnosisAnswer','checks','tests','prefix','suffix','starter','_path','diagnosisExplanation'}
        for task in TASKS:
            self.assertFalse(closed&public_task(task).keys(),task['id'])
        # Every question has precisely the four choices from the source.
        for task in TASKS:
            if task['group']=='Q':
                self.assertEqual(len(task['options']),4)
                self.assertEqual(grade_answer(task,task['answer'])['status'],'PASS')
    def test_prediction_all_originals_and_unfamiliar_variants(self):
        for task in [t for t in TASKS if t['group']=='P']:
            for variant in range(len(task['variants'])+1):
                current=with_variant(task,variant)
                body=dict(output=current['expectedOutput'],trace=current['traceAnswer'],explanation='I explain the value flow in my own words.',variant=variant)
                result=prediction(task,body)
                self.assertEqual((result['status'],result['pointsEarned']),('PASS',2),(task['id'],variant))
                body['trace']={k:'wrong' for k in current['traceAnswer']}
                body['explanation']='const reference temporary copy stream ' * 8
                self.assertEqual(prediction(task,body)['pointsEarned'],1)
                body['output']='wrong';self.assertEqual(prediction(task,body)['pointsEarned'],0)
    def test_console_numeric_comparison_and_error_protocol(self):
        # Errors must have diagnostics, no partial success output, and nonzero exit.
        bad=next(c for c in cases() if not c.get('valid'))
        self.assertFalse(evaluate(bad,dict(code=1,output='count=0\n',stderr='bad',timeout=False))[0])
        self.assertFalse(evaluate(bad,dict(code=0,output='',stderr='bad',timeout=False))[0])
        self.assertTrue(evaluate(bad,dict(code=1,output='',stderr='bad',timeout=False))[0])
    def test_compile_only_does_not_credit_v2(self):
        with patch('backend.day01_v2.scoring.storage.history',return_value=[dict(task='d01-v2-a01',mode='compile',status='COMPILED',pointsEarned=10)]):
            result=summary();self.assertEqual(result['earned'],0);self.assertEqual(result['passed'],0)
            self.assertEqual(result['maximum'],130);self.assertTrue(result['critical'])
        all_pass=[dict(task=t['id'],mode='test',status='PASS',compiled=True,pointsEarned=t['maxPoints']) for t in TASKS]
        with patch('backend.day01_v2.scoring.storage.history',return_value=all_pass):
            self.assertEqual(summary()['earned'],130);self.assertEqual(summary()['state'],'Все задания отмечены выполненными')
            all_pass[0]=dict(all_pass[0],status='FAIL',pointsEarned=0)
            self.assertNotEqual(summary()['state'],'Все задания отмечены выполненными')

class StereoLabRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get('MASTERY_TEST_COMPILER')!='1':raise unittest.SkipTest('Optional compiler checks')
        if not doctor()['available']:raise unittest.SkipTest('C++ compiler unavailable')
    def assert_pass(self,task,files):
        result=grade(task,files)
        self.assertEqual(result['status'],'PASS',(task['id'],result))
        self.assertEqual(result['pointsEarned'],task['maxPoints'])
        return result
    def test_all_fourteen_syntax_contracts_and_partial_credit(self):
        for n,source in S_REFERENCES.items():
            self.assert_pass(get_task(f'd01-v2-s{n:02}'),code(source))
        t=get_task('d01-v2-s10');wrong=code('double operator()(double x)const{return a_*x+b_+c_;}')
        result=grade(t,wrong);self.assertTrue(result['signaturePassed']);self.assertEqual(result['pointsEarned'],1);self.assertEqual(result['status'],'FAIL')
        self.assertEqual(grade(t,code(S_REFERENCES[10]),'compile')['pointsEarned'],0)
    def test_six_diagnoses_and_repairs(self):
        for task in [t for t in TASKS if t['group']=='D']:
            with patch('backend.day01_v2.grading.latest_diagnosis',return_value=None):
                self.assertEqual(grade(task,code(debug_reference(task)))['status'],'ANALYSIS_REQUIRED')
            record_diagnosis(task)
            self.assert_pass(task,code(debug_reference(task)))
        task=get_task('d01-v2-d06');record_diagnosis(task)
        wrong=debug_reference(task).replace('<=1e-9','<=0.5')
        self.assertEqual(grade(task,code(wrong))['status'],'FAIL')
    def test_all_component_and_integration_references_compile_and_run(self):
        with seeded_components():
            for suffix in ('a01','a02','a03','b01','b02','c01'):
                task=get_task('d01-v2-'+suffix)
                result=self.assert_pass(task,reference_files(task['id']))
                self.assertTrue(result['tests'])
                if suffix=='c01':self.assertGreaterEqual(len(result['tests']),14)
    def test_autonomous_fixtures_and_real_integration_dependencies(self):
        # A2/A3 do not depend on unfinished learner A1/A2.
        for suffix in ('a02','a03'):
            task=get_task('d01-v2-'+suffix);self.assert_pass(task,reference_files(task['id']))
        task=get_task('d01-v2-b02')
        result=grade(task,reference_files(task['id']))
        self.assertEqual(result['status'],'DEPENDENCY_ERROR');self.assertIn('d01-v2-a01',result['missingDependencies'])
        with seeded_components():
            path=student_dir(get_task('d01-v2-a02'))/'solution.hpp'
            original=path.read_text(encoding='utf-8')
            path.write_text(original.replace('a_*s.left()+b_*s.right()','0.0*s.left()+0.0*s.right()'),encoding='utf-8')
            result=grade(task,reference_files(task['id']))
            self.assertNotEqual(result['status'],'PASS');self.assertEqual(len(result['dependencyHashes']),3)
    def test_deliberate_component_and_pipeline_mutants_fail(self):
        mutations={
            'a01':lambda s:s.replace('<=1e-9','<=0.5'),
            'a02':lambda s:s.replace('a_*r.a_+b_*r.c_','a_*r.a_+c_*r.b_'),
            'a03':lambda s:s.replace('i>=used_','i>=4'),
            'b01':lambda s:s.replace('return in;','value=StereoSample(0,0);return in;',1),
            'b02':lambda s:s.replace('second*first','first*second'),
        }
        with seeded_components():
            for suffix,mutate in mutations.items():
                task=get_task('d01-v2-'+suffix);files=reference_files(task['id']);changed=mutate(files['solution.hpp'])
                self.assertNotEqual(changed,files['solution.hpp'],suffix);files['solution.hpp']=changed
                result=grade(task,files);self.assertTrue(result['compiled'],(suffix,result));self.assertNotEqual(result['status'],'PASS',(suffix,result));self.assertTrue(any(not t['passed'] for t in result['tests']))
            task=get_task('d01-v2-c01');files=reference_files(task['id'])
            files['solution.cpp']=files['solution.cpp'].replace('AudioBlock input;','out<<"count="<<count<<"\\n"; AudioBlock input;')
            result=grade(task,files);self.assertTrue(result['compiled'],result);self.assertEqual(result['status'],'FAIL');self.assertTrue(result['criticalFailures'])
    def test_no_dynamic_resources_or_container_substitution(self):
        task=get_task('d01-v2-a01')
        for source in ('int* value=new int(1);','template<class T> class Other{};','std::vector<int> values;'):
            result=grade(task,code(source));self.assertEqual(result['status'],'STATIC_ERROR');self.assertEqual(result['pointsEarned'],0)
    def test_stdin_and_separate_stderr_do_not_change_existing_runner(self):
        result=run_process([sys.executable,'-c','import sys;print(sys.stdin.read());print("diagnostic",file=sys.stderr)'],DATA,stdin_text='input data',separate_stderr=True)
        self.assertEqual(result['code'],0);self.assertIn('input data',result['output']);self.assertNotIn('diagnostic',result['output']);self.assertIn('diagnostic',result['stderr'])
    def test_prediction_reference_outputs_match_real_cpp17_execution(self):
        folder=DATA/'.build/prediction-check';folder.mkdir(parents=True,exist_ok=True)
        for task in [t for t in TASKS if t['group']=='P']:
            for variant in range(len(task['variants'])+1):
                current=with_variant(task,variant);source=folder/'prediction.cpp';source.write_text(current['code'],encoding='utf-8')
                program=folder/'prediction.exe';built=compile_cpp([source],program)
                self.assertEqual(built['code'],0,(task['id'],variant,built['output']))
                result=execute(program);self.assertEqual(result['code'],0);self.assertEqual(result['output'].strip(),current['expectedOutput'],(task['id'],variant))
    def test_unsafe_debug_starter_is_never_executed(self):
        task=get_task('d01-v2-d05');record_diagnosis(task)
        with patch('backend.day01_v2.grading.execute') as execute_mock:
            result=grade(task,code(task['starter']))
            self.assertIn(result['status'],('REPAIR_REQUIRED','COMPILE_ERROR'));execute_mock.assert_not_called()

class StereoLabApiTests(unittest.TestCase):
    # Reuse only the HTTP helpers, not the original API tests.
    setUpClass=classmethod(legacy.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(legacy.ApiTests.tearDownClass.__func__)
    request=legacy.ApiTests.request
    def test_v2_private_keys_and_review_gates(self):
        for suffix in ('q01','p01','d01','a01','c01'):
            status,detail=self.request('/api/task/d01-v2-'+suffix);self.assertEqual(status,200)
            self.assertFalse({'tests','checks','answer','variants','traceAnswer','diagnosisAnswer'}&detail['task'].keys())
        self.assertEqual(self.request('/api/review/d01-v2-p06')[0],403)
        task=get_task('d01-v2-p06');body=dict(output=task['expectedOutput'],trace=task['traceAnswer'],explanation='Postfix preserves the old value before modifying x.',variant=0)
        status,result=self.request('/api/answer/'+task['id'],body);self.assertEqual(status,200);self.assertEqual(result['pointsEarned'],2)
        self.assertEqual(self.request('/api/review/'+task['id'])[1]['expectedOutput'],task['expectedOutput'])
        _,detail=self.request('/api/task/d01-v2-c01');self.assertIn('main.cpp',detail['files'])
        self.assertEqual(self.request('/api/archive/day-1')[0],404)
        self.assertEqual(self.request('/api/task/d1-s01')[0],404)
        _,score=self.request('/api/day01/summary');self.assertEqual(score['maximum'],130)

if __name__=='__main__':unittest.main()
