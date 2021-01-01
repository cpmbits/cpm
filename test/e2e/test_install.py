import unittest
import os
import shutil
import yaml

from cpm.api import create
from cpm.api import install
from cpm.api import build
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
        assert result == Result(0, 'installed bit test:1.0')

    def test_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        cpm_user_configuration.DEFAULT_CONFIGURATION['cpm_hub_url'] = 'http://localhost:8000'
        self.add_bit('test', '1.0')
        result = install.execute(['-s', 'http://localhost:8000'])
        assert result == Result(0, 'installed bits')

    def test_build_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        cpm_user_configuration.DEFAULT_CONFIGURATION['cpm_hub_url'] = 'http://localhost:8000'
        self.add_bit('test', '1.0')
        install.execute(['-s', 'http://localhost:8000'])
        build.execute([])

    def add_bit(self, name, version):
        with open(f'project.yaml') as stream:
            project_descriptor = yaml.safe_load(stream)
        project_descriptor['build']['bits'] = {
            name: version
        }
        with open(f'project.yaml', 'w') as stream:
            yaml.dump(project_descriptor, stream)
