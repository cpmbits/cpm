import unittest
import mock
import os
import shutil
import yaml
import re

from cpm.infrastructure import filesystem
from cpm.api import create
from cpm.api import install
from cpm.api import build
from cpm.api import publish
from cpm.api import test
from cpm.api.result import Result


class TestCpm(unittest.TestCase):
    PROJECT_NAME = 'test_project'
    PROJECT_NAME_FROM_TEMPLATE = 'templated_project'
    TEST_DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}'
    PROJECT_DIRECTORY = f'{TEST_DIRECTORY}/{PROJECT_NAME}'
    PROJECT_FROM_TEMPLATE_DIRECTORY = f'{TEST_DIRECTORY}/{PROJECT_NAME_FROM_TEMPLATE}'

    def setUp(self):
        self.cwd = os.getcwd()
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)
        shutil.rmtree(self.PROJECT_FROM_TEMPLATE_DIRECTORY, ignore_errors=True)
        os.chdir(self.TEST_DIRECTORY)
        create.execute([self.PROJECT_NAME])

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)
        shutil.rmtree(self.PROJECT_FROM_TEMPLATE_DIRECTORY, ignore_errors=True)

    def test_build(self):
        os.chdir(self.PROJECT_DIRECTORY)
        result = build.execute([])
        assert result.status_code == 0

    def test_build_with_user_defined_include(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_includes(['../environment'])
        self.add_main_with_user_include()
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
        self.set_libraries(['pthread', 'dl'])
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_build_after_recursive_bit_installation_for_target_not_described_by_bit(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('build', 'test', '1.0')
        self.set_libraries(['pthread', 'dl'])
        self.set_target_main('rpi4', 'main.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute(['rpi4'])
        assert result == Result(0, 'Build finished')

    def test_build_when_declared_bit_is_not_installed(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('build', 'test', '1.0')
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_build_from_docker_image(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_build_from_docker_image_with_ldflags(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_ldflags(['-Wl,--allow-multiple-definition'])
        self.set_target_ldflags('default', ['-Wl,-s'])
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_build_from_docker_image_with_toolchain_prefix(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_dockerfile('default', f'../environment/Dockerfile')
        self.set_toolchain_prefix('default', 'arm-linux-gnueabihf-')
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_run_tests_from_docker_image(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_target_test_image('default', 'cpmbits/ubuntu:20.04')
        self.set_test_ldflags(['-Wl,-s'])
        self.add_test('test_case.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 0

    def test_run_tests_using_dockerfile(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_target_test_dockerfile('default', f'../environment/Dockerfile')
        self.set_test_ldflags(['-Wl,-s'])
        self.add_test('test_case.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 0

    def test_build_from_docker_image_with_non_default_target(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_image('ubuntu', 'cpmbits/ubuntu:20.04')
        self.set_target_main('ubuntu', 'main.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_build_from_docker_image_with_post_build(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_post_build('default', [f'ls', f'rm build/{self.PROJECT_NAME}'])
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')
        assert not filesystem.file_exists(f'build/{self.PROJECT_NAME}')

    def test_build_from_dockerfile(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_dockerfile('default', f'../environment/Dockerfile')
        install.execute(['-s', 'http://localhost:8000'])
        result = build.execute([])
        assert result == Result(0, 'Build finished')

    def test_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.set_test_cflags(['-std=c++11'])
        self.add_test('test_case.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 0

    def test_specifying_test_file(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.set_test_cflags(['-std=c++11'])
        self.add_test('test_case1.cpp')
        self.add_test('test_case2.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute(['tests/test_case1.cpp'])
        assert result.status_code == 0

    def test_specifying_test_directory(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.set_test_cflags(['-std=c++11'])
        self.add_test('test_case1.cpp')
        self.add_test('test_case2.cpp')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute(['tests'])
        assert result.status_code == 0

    def test_using_reference_to_external_file_in_cflags(self):
        os.chdir(self.PROJECT_DIRECTORY)
        project_yaml = '''build:
  bits:
  packages:
name: test_project
targets:
  default:
    main: main.cpp
test:
  bits:
    cest: '1.0'
  cflags: !include test_cflags.yaml
version: 0.0.1
'''
        with open('project.yaml', 'w') as stream:
            stream.write(project_yaml)
        with open('test_cflags.yaml', 'w') as stream:
            yaml.dump(['-std=c++11'], stream)
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute(['tests'])
        assert result.status_code == 0

    def test_failing_test_after_recursive_bit_installation(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.add_test('test_case.cpp', fails=True)
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 1

    def test_failing_test_when_running_inside_docker_image(self):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.add_test('test_case.cpp', fails=True)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_target_test_image('default', 'cpmbits/ubuntu:20.04')
        install.execute(['-s', 'http://localhost:8000'])
        result = test.execute([])
        assert result.status_code == 1

    @mock.patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    @mock.patch('builtins.input')
    def test_publishing_template(self, user_input, getpass):
        user_input.return_value = 'user'
        getpass.return_value = 'password'
        os.chdir(self.PROJECT_DIRECTORY)
        self.set_target_dockerfile('default', f'../environment/Dockerfile')
        install.execute(['-s', 'http://localhost:8000'])
        result = publish.execute(['-t', '-s', 'http://localhost:8000'])
        assert result == Result(0, 'Project published')

    @mock.patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    @mock.patch('builtins.input')
    def test_creating_project_from_template(self, user_input, getpass):
        os.chdir(self.PROJECT_DIRECTORY)
        self.add_bit('test', 'cest', '1.0')
        self.add_test('test_case.cpp', fails=True)
        self.set_target_image('default', 'cpmbits/ubuntu:20.04')
        self.set_target_test_image('default', 'cpmbits/ubuntu:20.04')
        self.set_target_dockerfile('default', f'../environment/Dockerfile')
        user_input.return_value = 'user'
        getpass.return_value = 'password'
        publish.execute(['-t', '-s', 'http://localhost:8000'])
        os.chdir('..')
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)
        result = create.execute(['-s', 'http://localhost:8000', '-t', f'{self.PROJECT_NAME}:0.0.1', self.PROJECT_NAME_FROM_TEMPLATE])
        assert result == Result(0, f'Created project {self.PROJECT_NAME_FROM_TEMPLATE}')

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

    def add_test(self, file_name, fails=False):
        if not filesystem.directory_exists('tests'):
            filesystem.create_directory('tests')
        expect = 'false' if fails else 'true'
        filesystem.create_file(
            f'tests/{file_name}',
            '#include <cest/cest.h>\n'
            'using namespace cest;\n'
            'describe("Test Case", []() {\n'
            '    it("passes", []() {\n'
            f'        expect(true).toBe({expect});\n'
            '    });\n'
            '});\n'
        )

    def set_target_image(self, target_name, image):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'image': image})
        )

    def set_toolchain_prefix(self, target_name, toolchain_prefix):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'toolchain_prefix': toolchain_prefix})
        )

    def set_target_test_image(self, target_name, image):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'test_image': image})
        )

    def set_target_main(self, target_name, main):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'main': main})
        )

    def set_post_build(self, target_name, post_build):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'post_build': post_build})
        )

    def set_target_dockerfile(self, target_name, dockerfile):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'dockerfile': dockerfile})
        )

    def set_target_test_dockerfile(self, target_name, dockerfile):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'test_dockerfile': dockerfile})
        )

    def set_target_ldflags(self, target_name, ldflags):
        self.modify_descriptor(
            lambda descriptor: descriptor.setdefault('targets', {}).setdefault(target_name, {}).update({'ldflags': ldflags})
        )

    def set_includes(self, includes):
        self.modify_descriptor(
            lambda descriptor: descriptor['build'].update({'includes': includes})
        )

    def set_ldflags(self, ldflags):
        self.modify_descriptor(
            lambda descriptor: descriptor['build'].update({'ldflags': ldflags})
        )

    def set_libraries(self, libraries):
        self.modify_descriptor(
            lambda descriptor: descriptor['build'].update({'libraries': libraries})
        )

    def set_test_cflags(self, cflags):
        self.modify_descriptor(
            lambda descriptor: descriptor['test'].update({'cflags': cflags})
        )

    def set_test_ldflags(self, ldflags):
        self.modify_descriptor(
            lambda descriptor: descriptor['test'].update({'ldflags': ldflags})
        )

    def modify_descriptor(self, modify):
        with open(f'project.yaml') as stream:
            project_descriptor = yaml.safe_load(stream)
        modify(project_descriptor)
        with open(f'project.yaml', 'w') as stream:
            yaml.dump(project_descriptor, stream)

    def add_main_with_user_include(self):
        filesystem.create_file(
            f'main.cpp',
            '#include <user_include.h>\n'
            'int main(int argc, char *argv[]) {\n'
            '    return 0;\n'
            '}\n'
        )
