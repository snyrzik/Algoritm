"""The additive Day 1 lecture, source fidelity, and existing-course isolation."""
import hashlib
import http.client
import json
import sys
import threading
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_platform as legacy
from backend.catalog import ROOT, DATA, catalog, get_task, student_files
from backend.theory import CHECK_IDS, LECTURE, lecture
from backend.grading import grade
from backend.compiler import doctor, toolchain, run_process

SOURCE_SHA256 = 'e0608d2ffed33fef5b5d0fe45be5adcc12f906d3544d8b816d2af16012012eec'

class TheoryContentTests(unittest.TestCase):
    def test_original_markdown_is_preserved_in_full(self):
        source=(LECTURE/'theory.md').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),SOURCE_SHA256)
        data=lecture()
        self.assertEqual(''.join(s['markdown'] for s in data['sections']).encode('utf-8'),source)
        self.assertEqual(data['sourceSha256'],SOURCE_SHA256)
        self.assertEqual([s['chapter'] for s in data['sections'] if 'chapter' in s],[1,2,3,4])
        self.assertTrue(data['sections'][0]['markdown'].startswith('# Лекция № 1'))
        self.assertIn('Переход к полной практике',data['sections'][-1]['markdown'])
    def test_all_existing_days_and_tests_are_unchanged(self):
        protected=json.loads((ROOT/'tests/day01_theory_legacy.sha256.json').read_text(encoding='utf-8'))
        self.assertEqual(len(protected),763)
        for name,digest in protected.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),digest,name)
    def test_new_checks_do_not_replace_or_renumber_existing_tasks(self):
        old=catalog(); all_tasks=catalog(include_theory=True)
        self.assertEqual(len(old),292); self.assertEqual(len(all_tasks),296)
        self.assertEqual(sum(t['day']==1 for t in old),52)
        extra=[t for t in all_tasks if t['id'] not in {old_task['id'] for old_task in old}]
        self.assertEqual([t['id'] for t in extra],CHECK_IDS)
        self.assertEqual(sum(len(t['tests']) for t in extra),40)
        for i,task in enumerate(extra,1):
            self.assertEqual((task['day'],task['lecture'],task['chapter']),(1,1,i))
            self.assertEqual(task['section'],'lecture-theory')
            self.assertNotIn('class ',task['starter'])
            self.assertIn(task['prompt'],(LECTURE/'theory.md').read_bytes().decode('utf-8'))
    def test_lecture_metadata_does_not_expose_solutions(self):
        for task in lecture()['checks']:
            self.assertFalse({'tests','hints','answer','explanation'} & task.keys())
            self.assertTrue(task['id'].startswith('d1-l1-c'))
            self.assertNotIn('return ',task['starter'])

class TheoryApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=legacy.server.ThreadingHTTPServer(('127.0.0.1',0),legacy.server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def request(self,path,body=None,method='POST'):
        client=http.client.HTTPConnection('127.0.0.1',self.http.server_port,timeout=60)
        headers={'Content-Type':'application/json','X-Mastery-Token':legacy.server.TOKEN}
        client.request('GET' if body is None else method,path,body=None if body is None else json.dumps(body),headers=headers)
        response=client.getresponse();status=response.status;data=json.loads(response.read());client.close();return status,data
    def test_theory_route_is_only_for_day_one_lecture_one(self):
        status,data=self.request('/api/theory/day-1/lecture-1');self.assertEqual(status,200);self.assertEqual(len(data['checks']),4)
        self.assertEqual(self.request('/api/theory/day-2/lecture-1')[0],404)
        _,course=self.request('/api/course');self.assertEqual(len(course['tasks']),292)
    def test_new_check_uses_same_editor_api_and_adapter_allowlist(self):
        _,detail=self.request('/api/task/d1-l1-c01')
        self.assertEqual(detail['task']['section'],'lecture-theory');self.assertIn('test_adapter.hpp',detail['files'])
        files=detail['files'];files['test_adapter.hpp']='// learner selects their own method names\n'
        status,_=self.request('/api/files/d1-l1-c01',{'files':files,'revision':detail['revision']},method='PUT');self.assertEqual(status,200)
        _,loaded=self.request('/api/task/d1-l1-c01');self.assertEqual(loaded['files']['test_adapter.hpp'],files['test_adapter.hpp'])
        _,original=self.request('/api/task/d1-c01');self.assertNotIn('test_adapter.hpp',original['files'])
    def test_check_attempt_does_not_complete_original_practice(self):
        task=get_task('d1-l1-c03');files=student_files(task)
        result={'status':'FAIL','score':0,'mode':'test','tests':[]}
        legacy.storage.record(task['id'],'test',result,files)
        _,progress=self.request('/api/progress')
        self.assertTrue(any(a['task']==task['id'] for a in progress['attempts']))
        self.assertFalse(any(a['task']=='d1-c01' and a['status']=='PASS' for a in progress['attempts']))

# Contract-only declarations validate the harness and adapter, never a solution.
CONTRACTS={
1:'''class ScoreCounter {public: explicit ScoreCounter(int=0); int points()const; ScoreCounter& add(int);}; bool higher_score(const ScoreCounter&,const ScoreCounter&);''',
2:'''class Duration {public: explicit Duration(int);int seconds()const;Duration& operator+=(const Duration&);Duration& operator++();Duration operator++(int);Duration operator-()const;};Duration operator+(const Duration&,const Duration&);bool operator==(const Duration&,const Duration&);bool operator!=(const Duration&,const Duration&);''',
3:'''#include <cstddef>
class FixedHistory{public:FixedHistory(int,int,int,int);int& operator[](std::size_t);const int& operator[](std::size_t)const;int operator()(std::size_t,std::size_t)const;void swap_indices(std::size_t,std::size_t);};''',
4:'''#include <iostream>
class ClockTime{public:ClockTime(int,int);};std::ostream& operator<<(std::ostream&,const ClockTime&);std::istream& operator>>(std::istream&,ClockTime&);'''
}
class TheoryRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not doctor()['available']:raise unittest.SkipTest('C++ compiler unavailable')
    def test_all_four_contract_harnesses_compile(self):
        tc=toolchain()
        for chapter,source in CONTRACTS.items():
            task=get_task(f'd1-l1-c{chapter:02}')
            folder=DATA/'.build'/'theory-contracts'/str(chapter);folder.mkdir(parents=True,exist_ok=True)
            (folder/'solution.hpp').write_text(source,encoding='utf-8')
            for name,starter in task.get('starterFiles',{}).items():(folder/name).write_text(starter,encoding='utf-8')
            (folder/'candidate.hpp').write_text('#include "solution.hpp"\n'+task['suffix'],encoding='utf-8')
            harness=ROOT/'days/day-01-operators/tests'/f"{task['id']}.cpp"
            includes=[folder,ROOT/'tools']
            args=[tc['exe'],'/nologo','/std:c++17','/EHsc','/W4','/WX','/utf-8','/Zs',*[f'/I{p}' for p in includes],harness] if tc['kind']=='msvc' else [tc['exe'],'-std=c++17','-Wall','-Wextra','-Wconversion','-Wpedantic','-Werror','-fsyntax-only',*[f'-I{p}' for p in includes],harness]
            result=run_process(args,folder,tc['env'],30)
            self.assertEqual(result['code'],0,(task['id'],result['output']))
    def test_empty_starters_are_not_marked_pass(self):
        for task_id in CHECK_IDS:
            task=get_task(task_id)
            files={'solution.hpp':task['starter'],'solution.cpp':'','notes.md':'',**task.get('starterFiles',{})}
            result=grade(task,files)
            self.assertEqual(result['status'],'COMPILE_ERROR',(task_id,result))
            self.assertEqual(result['tests'],[])

if __name__=='__main__':unittest.main()
