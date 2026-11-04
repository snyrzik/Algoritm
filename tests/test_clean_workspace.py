import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_platform as platform
from backend import storage
from backend.catalog import ROOT,catalog,get_task
from tools.reset_workspace import reset_workspace

class CleanWorkspaceTests(unittest.TestCase):
    def test_only_current_day_one_material_is_available(self):
        tasks=[t for t in catalog() if t['day']==1]
        self.assertEqual(len(tasks),3)
        self.assertTrue(all(t['id'].startswith('l01-v3-p') for t in tasks))
        self.assertIsNone(get_task('d1-s01'))
        from tools.content import questions,syntax,practice,debugging
        from tools.content.common import TASKS
        self.assertTrue(all(t['day']!=1 for t in TASKS))
        for name in ('archive','quiz','syntax','prediction','debugging','practice-v2'):
            self.assertFalse((ROOT/'days/day-01-operators'/name).exists())
    def test_reset_checks_paths_and_removes_answers_and_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);student=root/'student';progress=root/'progress'
            (student/'day-01/task').mkdir(parents=True);progress.mkdir()
            (student/'README.md').write_text('keep');(progress/'.gitkeep').touch()
            (student/'day-01/task/solution.hpp').write_text('old answer')
            (progress/'mastery.sqlite3').write_text('old progress')
            (student/'day-01/task/unrelated.txt').write_text('keep')
            with self.assertRaises(ValueError):reset_workspace(root,apply=True)
            self.assertTrue((student/'day-01/task/solution.hpp').exists())
            (student/'day-01/task/unrelated.txt').unlink()
            result=reset_workspace(root,apply=True);self.assertEqual(result['files'],2)
            self.assertEqual(list(student.iterdir()),[student/'README.md'])
            self.assertEqual(list(progress.iterdir()),[progress/'.gitkeep'])
    def test_profile_identity_survives_restart_and_changes_after_reset(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp,patch('backend.storage.DATA',Path(temp)):
            first=storage.profile_id();self.assertEqual(first,storage.profile_id())
            reset_workspace(Path(temp),apply=True)
            self.assertNotEqual(first,storage.profile_id())

if __name__=='__main__':unittest.main()
