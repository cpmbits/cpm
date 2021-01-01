import unittest
import os
import shutil

from cpm.api import create
from cpm.api import install
from cpm.api.result import Result

from cpm.infrastructure import cpm_user_configuration


class TestInstall(unittest.TestCase):
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

    def test_bit_installation_from_command_line_passed_bit(self):
        os.chdir(self.PROJECT_DIRECTORY)
        cpm_user_configuration.DEFAULT_CONFIGURATION['cpm_hub_url'] = 'http://localhost:8000'
        result = install.execute(['-s', 'http://localhost:8000', 'test:1.0'])
        assert result == Result(0, 'installed bit')
