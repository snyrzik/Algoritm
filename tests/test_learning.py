"""Learner navigation never pretends to assess work or overwrite existing results."""
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend import storage

class LearningApiTests(unittest.TestCase):
    setUpClass=classmethod(platform.ApiTests.setUpClass.__func__)
    tearDownClass=classmethod(platform.ApiTests.tearDownClass.__func__)
    request=platform.ApiTests.request
    def test_bookmarks_and_resume_persist_independently_of_results(self):
        before=storage.history()
        status,value=self.request('/api/learning',{'bookmarks':['l01-v3-c01','l02-local-p01'],'lastPath':'theory/1/chapter-3'})
        self.assertEqual(status,200)
        _,loaded=self.request('/api/learning');self.assertEqual(value,loaded)
        self.request('/api/learning',{'lastPath':'task/l02-local-p01'})
        _,loaded=self.request('/api/learning');self.assertEqual(loaded['bookmarks'],['l01-v3-c01','l02-local-p01'])
        self.assertEqual(loaded['lastPath'],'task/l02-local-p01');self.assertEqual(storage.history(),before)
        self.request('/api/learning',{'bookmarks':[]})
        _,loaded=self.request('/api/learning');self.assertEqual(loaded['bookmarks'],[])
    def test_invalid_and_cross_origin_updates_are_rejected(self):
        for body in [{'bookmarks':['unknown']},{'bookmarks':'d2-c01'},{'lastPath':'https://example.com'},{'lastPath':'task/../../secret'},{'lastPath':'theory/2/chapter-5'},{'score':100}]:
            self.assertEqual(self.request('/api/learning',body)[0],400,body)
        self.assertEqual(self.request('/api/learning',{'bookmarks':[]},token=False)[0],403)
        self.assertEqual(self.request('/api/learning',{'lastPath':'module/2'},origin='http://evil.example')[0],403)
    def test_course_includes_every_lecture_check_and_progress_keeps_reading_separate(self):
        _,course=self.request('/api/course');ids={task['id'] for task in course['tasks']}
        self.assertEqual(len(ids),21)
        self.assertTrue(all(f'l01-v3-c{i:02}' in ids for i in range(1,6)))
        _,progress=self.request('/api/progress');self.assertIn('reading',progress)
        self.assertIsInstance(progress['reading'],list)
    def test_parallel_startup_and_navigation_updates_do_not_lock_database(self):
        calls=[('/api/learning',{'lastPath':'module/2'}),('/api/learning',None),('/api/progress',None),('/api/theory/day-1/lecture-1',None)]*5
        with ThreadPoolExecutor(max_workers=8) as pool:
            values=list(pool.map(lambda item:self.request(item[0],item[1]),calls))
        self.assertTrue(all(status==200 for status,_ in values),values)

if __name__=='__main__':unittest.main()
