import unittest
import os
import shutil

from cpm.infrastructure import filesystem
from cpm.api import create
from cpm.api import test


class TestTest(unittest.TestCase):
    PROJECT_NAME = 'test_project'
    TEST_DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}'
    PROJECT_DIRECTORY = f'{TEST_DIRECTORY}/{PROJECT_NAME}'

    def setUp(self):
        self.cwd = os.getcwd()
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)
        os.chdir(self.TEST_DIRECTORY)
        create.execute([self.PROJECT_NAME])
        self.create_dummy_test()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.PROJECT_DIRECTORY)

    def test_test(self):
        os.chdir(self.PROJECT_DIRECTORY)
        result = test.execute([])
        assert result.status_code == 0

    def create_dummy_test(self):
        filesystem.create_directory(f'{self.PROJECT_DIRECTORY}/tests')
        filesystem.create_file(
            f'{self.PROJECT_DIRECTORY}/tests/test_one.cpp',
            'int main(void) { return 0; }'
        )
