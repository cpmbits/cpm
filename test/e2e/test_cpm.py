import unittest
import os
import shutil
import yaml

from cpm.infrastructure import filesystem
from cpm.api import create
from cpm.api import install
from cpm.api import build
from cpm.api import test
from cpm.api.result import Result


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

    def test_build(self):
        os.chdir(self.PROJECT_DIRECTORY)
        result = build.execute([])
        assert result.status_code == 0

    def test_bit_installation_from_command_line_passed_bit(self):
        os.chdir(self.PROJECT_DIRECTORY)
        result = install.execute(['-s', 'http://localhost:8000', 'test:1.0'])
        assert result == Result(0, 'installed bit test:1.0')

    def test_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('build', 'test', '1.0')
        result = install.execute(['-s', 'http://localhost:8000'])
        assert result == Result(0, 'installed bits')

    def test_build_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('build', 'test', '1.0')
        install.execute(['-s', 'http://localhost:8000'])
        build.execute([])

    def test_build_from_docker_image(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        install.execute(['-s', 'http://localhost:8000'])
        build.execute([])

    def test_build_from_dockerfile(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_dockerfile('default', f'../environment')
        install.execute(['-s', 'http://localhost:8000'])
        build.execute([])

    def test_test_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.add_test()
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 0

    def test_failing_test_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.add_test(fails=True)
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 1

    def add_bit(self, plan, name, version):
        with open(f'project.yaml') as stream:
            project_descriptor = yaml.safe_load(stream)
        if plan not in project_descriptor or not project_descriptor[plan]:
            project_descriptor[plan] = {}
        project_descriptor[plan]['bits'] = {
            name: version
        }
        with open(f'project.yaml', 'w') as stream:
            yaml.dump(project_descriptor, stream)

    def add_test(self, fails=False):
        filesystem.create_directory('tests')
        expect = 'false' if fails else 'true'
        filesystem.create_file(
            'tests/test_case.cpp',
            '#include <cest/cest.h>\n'
            'using namespace cest;\n'
            'describe("Test Case", []() {\n'
            '    it("passes", []() {\n'
            f'        expect(true).toBe({expect});\n'
            '    });\n'
            '});\n'
        )

    def set_target_image(self, target_name, image):
        with open(f'project.yaml') as stream:
            project_descriptor = yaml.safe_load(stream)
        project_descriptor.setdefault('targets', {}).setdefault(target_name, {})['image'] = image
        with open(f'project.yaml', 'w') as stream:
            yaml.dump(project_descriptor, stream)

    def set_target_dockerfile(self, target_name, dockerfile):
        with open(f'project.yaml') as stream:
            project_descriptor = yaml.safe_load(stream)
        project_descriptor.setdefault('targets', {}).setdefault(target_name, {})['dockerfile'] = dockerfile
        with open(f'project.yaml', 'w') as stream:
            yaml.dump(project_descriptor, stream)
