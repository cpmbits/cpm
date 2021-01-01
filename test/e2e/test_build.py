import unittest
import os
import shutil

from cpm.api import create
from cpm.api import build


class TestBuild(unittest.TestCase):
    PROJECT_NAME = 'test_project'
    TEST_DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}'
    PROJECT_DIRECTORY = f'{TEST_DIRECTORY}/{PROJECT_NAME}'

    def setUp(self):
        self.cwd = os.getcwd()
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)
        os.chdir(self.TEST_DIRECTORY)
        create.execute([self.PROJECT_NAME])

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.PROJECT_DIRECTORY)

    def test_build(self):
        os.chdir(self.PROJECT_DIRECTORY)
        result = build.execute([])
        assert result.status_code == 0
