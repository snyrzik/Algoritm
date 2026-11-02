"""Infrastructure tests use disposable data; they never solve student exercises."""
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest

TEMP=tempfile.TemporaryDirectory(prefix='cpp-mastery-tests-')
os.environ['MASTERY_DATA']=TEMP.name
from backend.catalog import ROOT,DATA,catalog,get_task,public_task,student_files
from backend.compiler import doctor,compile_cpp,execute,run_process
from backend.grading import grade,grade_answer,revision,static_review
from backend import storage,server

def fixture(body, tests=None, memory=False):
    tests=tests or [('answer','CHECK(answer()==42);')]
    day=DATA/'fixtures'/'day-smoke'; folder=day/'practice'/'smoke'; folder.mkdir(parents=True,exist_ok=True)
    (day/'tests').mkdir(exist_ok=True)
    snippets='\n'.join(f'void test{i}(){{{source}}}' for i,(_,source) in enumerate(tests))
    dispatch='\n'.join(f'case {i}:test{i}();break;' for i in range(len(tests)))
    (day/'tests'/'smoke.cpp').write_text('#include "candidate.hpp"\n#include <iostream>\n#include <string>\n#include "support.hpp"\n'+snippets+'\nint main(int argc,char** argv){if(argc!=2)return 2;try{long before=mastery_memory::live;switch(std::stoi(argv[1])){'+dispatch+'default:return 2;}mastery_memory::fail_after=-1;CHECK(mastery_memory::live==before);return 0;}catch(const std::exception& e){std::cerr<<e.what();return 1;}}',encoding='utf-8')
    task={'id':'smoke','day':1,'kind':'C','_path':str(folder),'memory':memory,'tests':[{'name':n,'category':'functional'} for n,_ in tests]}
    return task,{'solution.hpp':body,'solution.cpp':'','notes.md':''}

class ContentTests(unittest.TestCase):
    def test_counts_and_unique_ids(self):
        items=catalog(); self.assertEqual(len(items),288); self.assertEqual(len({t['id'] for t in items}),288)
        for day,minimums in {1:[16,14,6,6,6],2:[15,18,5,8,8],3:[15,20,5,8,9],4:[18,20,5,8,8],5:[30,20,5,10,3]}.items():
            for kind,count in zip('QSPDC',minimums): self.assertGreaterEqual(sum(t['day']==day and t['kind']==kind for t in items),count)
    def test_questions_have_valid_answers_and_explanations(self):
        for t in catalog():
            self.assertGreater(len(t['prompt']),20,t['id'])
            if t['kind'] in ('Q','P'):
                if t.get('runner')=='prediction':
                    self.assertTrue(t['expectedOutput']);self.assertTrue(t['traceAnswer']);continue
                self.assertTrue(t['answer']); self.assertEqual(len(t['options']),len(t['optionExplanations']))
                self.assertTrue(all(type(i) is int and 0<=i<len(t['options']) for i in t['answer']))
                self.assertGreater(len(t['explanation']),30)
    def test_public_catalog_does_not_leak_answers(self):
        for t in catalog():
            public=public_task(t)
            self.assertFalse({'answer','explanation','optionExplanations','tests','hints','_path'}&public.keys())
    def test_every_cpp_task_has_real_harness(self):
        for t in catalog():
            if t['kind'] in ('S','D','C'):
                if t.get('runner')=='console':
                    from backend.day01_v2.console import cases
                    self.assertGreaterEqual(len(cases()),10);continue
                self.assertTrue(t['tests'],t['id'])
                day=next(p for p in Path(t['_path']).parents if p.name.startswith('day-'))
                harness=day/('practice-v2/tests' if t.get('version')==2 else 'tests')/f"{t['id']}.cpp"
                self.assertTrue(harness.is_file(),t['id'])
                self.assertIn('candidate.hpp',harness.read_text(encoding='utf-8'))
                if t['kind']=='C':self.assertGreaterEqual(len(t['tests']),3,t['id'])
    def test_generation_does_not_overwrite_student_code(self):
        t=get_task('d1-s01'); student_files(t)
        path=DATA/t['filePath'];path.write_text('// learner content',encoding='utf-8')
        self.assertEqual(student_files(t)['solution.hpp'],'// learner content')
    def test_exact_multiselect_grading(self):
        t=get_task('d1-q02'); self.assertEqual(grade_answer(t,[0,2])['status'],'PASS'); self.assertEqual(grade_answer(t,[0])['score'],0)
        with self.assertRaises(ValueError):grade_answer(t,[])
        with self.assertRaises(ValueError):grade_answer(t,[True])
    def test_rules_ignore_comments(self):
        task={'staticChecks':['no_containers','no_rtti']}
        self.assertEqual(static_review(task,{'solution.hpp':'// std::vector; dynamic_cast<X>(x)\n/* typeid(T) */'}),[])
        self.assertEqual(len(static_review(task,{'solution.hpp':'std::vector<int> x; auto y=typeid(x);'})),2)

class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=doctor()
        if not cls.d['available']:raise unittest.SkipTest('C++ compiler unavailable: '+cls.d['details'])
    def test_real_success_and_independent_failure(self):
        t,f=fixture('int answer(){return 42;}', [('correct','CHECK(answer()==42);'),('deliberate mismatch','CHECK(answer()==41);')])
        r=grade(t,f);self.assertTrue(r['compiled'],r.get('compilation'));self.assertEqual(r['status'],'FAIL');self.assertEqual(r['score'],50);self.assertEqual([x['passed'] for x in r['tests']],[True,False])
    def test_concurrent_compiler_detection(self):
        from concurrent.futures import ThreadPoolExecutor
        from backend.compiler import _doctor_cached
        _doctor_cached.cache_clear()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _:doctor(),range(4)))
        self.assertTrue(all(r['available'] for r in results),results)
        self.assertTrue(all(r==results[0] for r in results))
    def test_success_and_compile_only_not_pass(self):
        t,f=fixture('int answer(){return 42;}')
        self.assertEqual(grade(t,f,'compile')['status'],'COMPILED')
        r=grade(t,f);self.assertEqual(r['status'],'PASS',r)
    def test_compile_diagnostics_and_missing_header(self):
        t,f=fixture('std::size_t answer(){return 42;}')
        r=grade(t,f);self.assertEqual(r['status'],'COMPILE_ERROR');self.assertTrue(r['compilation']);self.assertEqual(r['tests'],[])
    def test_multiple_source_files(self):
        t,f=fixture('int answer();');f['solution.cpp']='#include "solution.hpp"\nint answer(){return 42;}'
        r=grade(t,f);self.assertEqual(r['status'],'PASS',r)
    def test_new_delete_leak_detection(self):
        t,f=fixture('int answer(){int* p=new int(42);return *p;}')
        r=grade(t,f);self.assertEqual(r['status'],'FAIL');self.assertIn('mastery_memory::live',r['tests'][0]['output'])
    def test_fault_injection_and_no_leak(self):
        t,f=fixture('#include <new>\nvoid allocate(){int* p=new int[3];delete[] p;}', [('bad_alloc','mastery_memory::fail_after=0; expect_throw<std::bad_alloc>([]{allocate();});')])
        r=grade(t,f);self.assertEqual(r['status'],'PASS',r)
    def test_sanitizer_detects_heap_overflow(self):
        if not self.d['addressSanitizer']: self.skipTest('ASan unavailable')
        t,f=fixture('int answer(){int* p=new int[1];volatile int index=2;p[index]=42;int v=p[index];delete[] p;return v;}',memory=True)
        r=grade(t,f);self.assertTrue(r['compiled'],r);self.assertEqual(r['status'],'FAIL');self.assertIn('AddressSanitizer',r['tests'][0]['output'])
    def test_process_timeout_and_output_bound(self):
        import sys
        result=run_process([sys.executable,'-c','while True: pass'],DATA,timeout=.2)
        self.assertTrue(result['timeout']);self.assertNotEqual(result['code'],0)
        result=run_process([sys.executable,'-c','import sys;sys.stdout.write("x"*1000000)'],DATA,timeout=3)
        self.assertTrue(result['truncated']);self.assertLess(len(result['output']),50000)
    def test_failed_task_does_not_block_next(self):
        t,f=fixture('broken C++ syntax');self.assertEqual(grade(t,f)['status'],'COMPILE_ERROR')
        t,f=fixture('int answer(){return 42;}');self.assertEqual(grade(t,f)['status'],'PASS')

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.port=cls.http.server_port
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def request(self,path,body=None,token=True,origin=None,method='POST'):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=60);headers={}
        if body is not None:headers={'Content-Type':'application/json','X-Mastery-Token':server.TOKEN if token else ''}
        if origin:headers['Origin']=origin
        c.request('GET' if body is None else method,path,body=None if body is None else json.dumps(body),headers=headers)
        r=c.getresponse();status=r.status;data=json.loads(r.read());c.close();return status,data
    def test_local_session_and_catalog(self):
        status,data=self.request('/api/session');self.assertEqual(status,200);self.assertEqual(data['token'],server.TOKEN)
        status,data=self.request('/api/course');self.assertEqual(len(data['tasks']),288);self.assertEqual(len(data['days']),5)
    def test_cross_origin_and_missing_token_rejected(self):
        status,_=self.request('/api/answer/d1-q01',{'answer':[1]},token=False);self.assertEqual(status,403)
        status,_=self.request('/api/answer/d1-q01',{'answer':[1]},origin='http://evil.example');self.assertEqual(status,403)
    def test_no_answer_before_attempt_then_persistent_result(self):
        status,_=self.request('/api/review/d5-q30');self.assertEqual(status,403)
        status,data=self.request('/api/answer/d5-q30',{'answer':[1]});self.assertEqual(data['status'],'PASS')
        status,data=self.request('/api/review/d5-q30');self.assertEqual(data['answer'],[1]);self.assertTrue(storage.history('d5-q30'))
    def test_conflict_does_not_overwrite_external_edit(self):
        _,detail=self.request('/api/task/d1-s02');files=detail['files'];files['solution.hpp']='// draft'
        path=DATA/detail['task']['filePath'];path.write_text('// external',encoding='utf-8')
        status,_=self.request('/api/files/d1-s02',{'files':files,'revision':detail['revision']},method='PUT')
        self.assertEqual(status,409);self.assertEqual(path.read_text(encoding='utf-8'),'// external')
    def test_file_allowlist_and_save(self):
        _,detail=self.request('/api/task/d1-s03');files=detail['files'];files['../evil']='no'
        status,_=self.request('/api/files/d1-s03',{'files':files,'revision':detail['revision']},method='PUT');self.assertEqual(status,400)
        del files['../evil'];files['notes.md']='Reasoning from the learner.'
        status,saved=self.request('/api/files/d1-s03',{'files':files,'revision':detail['revision']},method='PUT');self.assertEqual(status,200);self.assertEqual(saved['revision'],revision(files))
    def test_exam_hints_and_review_are_deferred(self):
        _,e=self.request('/api/exam/start',{'timed':True});self.assertEqual(len(set(e['tasks'])),20)
        status,_=self.request('/api/hint/d5-s01',{'level':1});self.assertEqual(status,403)
        status,r=self.request('/api/answer/d5-q01',{'answer':[0]});self.assertEqual(status,200)
        _,r=self.request('/api/review/d5-q01');self.assertTrue(r['deferred'])
        self.request('/api/exam/finish',{});_,r=self.request('/api/review/d5-q01');self.assertEqual(r['answer'],[0])
        self.request('/api/exam/start',{'timed':False})
    def test_snapshots_and_hint_counts(self):
        self.request('/api/hint/d1-q03',{'level':1});self.request('/api/answer/d1-q03',{'answer':[2]})
        entry=storage.history('d1-q03')[0];self.assertEqual(entry['hintsUsed'],1)
        _,snapshot=self.request('/api/snapshot/'+str(entry['id']));self.assertEqual(snapshot['files']['answer'],[2])
    def test_syntax_deadline_survives_reload_and_blocks_late_run(self):
        import time
        self.request('/api/exam/start',{'timed':True})
        _,first=self.request('/api/task/d5-s01');_,second=self.request('/api/task/d5-s01')
        self.assertEqual(first['syntaxDeadline'],second['syntaxDeadline'])
        self.assertGreater(first['syntaxDeadline'],time.time())
        with storage.connect() as db:db.execute('UPDATE syntax_clock SET started=?',(time.time()-300,))
        status,r=self.request('/api/run/d5-s01',{'mode':'test'})
        self.assertEqual(status,400);self.assertIn('4 минуты',r['error'])
        self.request('/api/exam/start',{'timed':False})

if __name__=='__main__':unittest.main()
