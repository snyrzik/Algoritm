"""Platform infrastructure checks use disposable data and never execute learner C++."""
import http.client
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path

TEMP=tempfile.TemporaryDirectory(prefix='cpp-mastery-tests-')
os.environ['MASTERY_DATA']=TEMP.name
from backend.catalog import ROOT,DATA,catalog,get_task,public_task,student_files
from backend.answers import revision
from backend import storage,server

class ContentTests(unittest.TestCase):
    def test_current_program_has_four_new_lectures(self):
        items=catalog(True);self.assertEqual(len(items),28);self.assertEqual(len({t['id'] for t in items}),28)
        self.assertEqual({n:sum(t['day']==n for t in items) for n in (1,2,3,4)},{1:8,2:6,3:7,4:7})
        self.assertTrue(all(t['required'] for t in items))
        self.assertTrue(all(t['id'].startswith(('l01-v3-','l02-local-','l03-local-','l04-local-')) for t in items))
    def test_public_catalog_has_conditions_and_no_answer_keys(self):
        for task in catalog(True):
            self.assertGreater(len(task['prompt']),20)
            self.assertFalse({'answer','explanation','optionExplanations','tests','hints','_path'}&public_task(task).keys())
    def test_existing_student_file_is_never_overwritten(self):
        task=get_task('l01-v3-c01');student_files(task);path=DATA/task['filePath'];path.write_text('// learner content',encoding='utf-8')
        self.assertEqual(student_files(task)['solution.hpp'],'// learner content')

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.port=cls.http.server_port
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def request(self,path,body=None,token=True,origin=None,method='POST'):
        client=http.client.HTTPConnection('127.0.0.1',self.port,timeout=60);headers={}
        if body is not None:headers={'Content-Type':'application/json','X-Mastery-Token':server.TOKEN if token else ''}
        if origin:headers['Origin']=origin
        client.request('GET' if body is None else method,path,body=None if body is None else json.dumps(body),headers=headers)
        response=client.getresponse();status=response.status;data=json.loads(response.read());client.close();return status,data
    def test_local_session_and_current_catalog(self):
        status,value=self.request('/api/session');self.assertEqual(status,200);self.assertEqual(value['token'],server.TOKEN)
        _,value=self.request('/api/course');self.assertEqual(len(value['tasks']),28);self.assertEqual([m['id'] for m in value['days']],[1,2,3,4])
    def test_cross_origin_and_missing_token_rejected(self):
        body={'stage':'reflection','status':'SELF_CHECKED'}
        self.assertEqual(self.request('/api/lecture-state/l02-local-c03',body,token=False)[0],403)
        self.assertEqual(self.request('/api/lecture-state/l02-local-c03',body,origin='http://evil.example')[0],403)
    def test_conflict_does_not_overwrite_external_edit(self):
        _,detail=self.request('/api/task/l01-v3-c03');files=detail['files'];files['solution.hpp']='// browser draft'
        path=DATA/detail['task']['filePath'];path.write_text('// external edit',encoding='utf-8')
        self.assertEqual(self.request('/api/files/l01-v3-c03',{'files':files,'revision':detail['revision']},method='PUT')[0],409)
        self.assertEqual(path.read_text(encoding='utf-8'),'// external edit')
    def test_file_allowlist_and_save(self):
        _,detail=self.request('/api/task/l01-v3-c02');files=detail['files'];files['../escape']='no'
        self.assertEqual(self.request('/api/files/l01-v3-c02',{'files':files,'revision':detail['revision']},method='PUT')[0],400)
        del files['../escape'];files['notes.md']='Independent learner explanation.'
        status,value=self.request('/api/files/l01-v3-c02',{'files':files,'revision':detail['revision']},method='PUT');self.assertEqual(status,200);self.assertEqual(value['revision'],revision(files))
    def test_snapshots_and_previous_results_remain_readable(self):
        saved=storage.record('d5-q01','answer',{'status':'PASS','score':100},{'notes.md':'Earlier learner work'})
        _,value=self.request('/api/snapshot/'+str(saved['attemptId']));self.assertEqual(value['files']['notes.md'],'Earlier learner work')
        self.assertEqual(self.request('/api/task/d5-q01')[0],404)
        _,value=self.request('/api/progress');self.assertTrue(any(item['task']=='d5-q01' for item in value['attempts']))
    def test_timers_and_old_cpp_execution_are_retired(self):
        self.assertEqual(self.request('/api/exam/start',{'timed':True})[0],410)
        self.assertEqual(self.request('/api/exam/finish',{})[0],410)
        self.assertEqual(self.request('/api/doctor')[0],410)
        self.assertEqual(self.request('/api/run/l01-v3-c01',{'mode':'test'})[0],410)
        self.assertEqual(self.request('/api/answer/l02-local-c01',{'answer':[0]})[0],400)

if __name__=='__main__':unittest.main()
