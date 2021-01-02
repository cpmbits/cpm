import unittest
from mock import MagicMock
from mock import patch

import os

from cpm.domain.compilation_service import CompilationService
from cpm.domain.project_commands import DockerImageNotFound
from cpm.domain.project.project import Project, Target
from cpm.domain.project.project_descriptor_parser import NotACpmProject


class TestCompilationService(unittest.TestCase):
    def setUp(self):
        self.cmakelists_builder = MagicMock()
        self.project_loader = MagicMock()
        self.project_builder = MagicMock()
        self.compilation_service = CompilationService(self.project_loader, self.cmakelists_builder, self.project_builder)

    def test_compilation_service_fails_when_project_loader_fails_to_load_project(self):
        self.project_loader.load.side_effect = NotACpmProject

        self.assertRaises(NotACpmProject, self.compilation_service.build)
        self.assertRaises(NotACpmProject, self.compilation_service.update)
        self.project_loader.load.assert_called()

    def test_compilation_service_generates_compilation_recipe_from_project_sources_and_compiles_project(self):
        project = Project('ProjectName')
        self.project_loader.load.return_value = project

        self.compilation_service.build()

        self.project_loader.load.assert_called_once()
        self.cmakelists_builder.build.assert_called_once_with(project, 'default')
        self.project_builder.build.assert_called_once_with(project, 'default')

    def test_compilation_service_only_generates_compilation_recipe_when_updating(self):
        project = Project('ProjectName')
        self.project_loader.load.return_value = project

        self.compilation_service.update()

        self.project_loader.load.assert_called_once()
        self.cmakelists_builder.build.assert_called_once_with(project, 'default')

    def test_clean_fails_when_project_loader_fails_to_load_project(self):
        self.project_loader.load.side_effect = NotACpmProject
        self.assertRaises(NotACpmProject, self.compilation_service.clean)
        self.project_loader.load.assert_called_once()

    def test_clean_uses_cmake_recipe_to_clean_project(self):
        self.compilation_service.clean()

        self.project_loader.load.assert_called_once()
        self.project_builder.clean.assert_called_once()

    @patch('cpm.domain.compilation_service.docker')
    def dtest_it_uses_docker_to_build_for_the_specified_target(self, docker):
        project = Project('Project')
        self.project_loader.load.return_value = project
        docker_client = MagicMock()
        container = MagicMock()
        container.logs.return_value = []
        docker_client.containers.return_value = container
        docker.from_env.return_value = docker_client

        self.compilation_service.build_target('raspberrypi4:64')

        self.project_loader.load.assert_called_once()
        docker_client.containers.run.assert_called_once_with(
            f'cpmbits/raspberrypi4:64',
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )

    @patch('cpm.domain.compilation_service.docker')
    def dtest_it_uses_image_declared_for_target(self, docker):
        project = Project('Project')
        target = Target('ubuntu')
        target.image = 'cpmhub/ubuntu'
        project.targets.append(target)
        docker_client = MagicMock()
        container = MagicMock()
        container.logs.return_value = []
        docker_client.containers.return_value = container
        docker.from_env.return_value = docker_client
        self.project_loader.load.return_value = project

        self.compilation_service.build_target('ubuntu')

        self.project_loader.load.assert_called_once()
        docker_client.containers.run.assert_called_once_with(
            f'cpmhub/ubuntu',
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )

    @patch('cpm.domain.compilation_service.docker')
    def dtest_it_raises_an_exception_when_docker_image_is_not_found(self, docker):
        project = Project('Project')
        target = Target('ubuntu')
        target.image = 'cpmhub/ubuntu'
        project.targets.append(target)
        docker_client = MagicMock()
        docker.errors.ImageNotFound = RuntimeError
        docker_client.images.pull.side_effect = docker.errors.ImageNotFound
        docker.from_env.return_value = docker_client
        self.project_loader.load.return_value = project

        self.assertRaises(DockerImageNotFound, self.compilation_service.build_target, 'ubuntu')

        self.project_loader.load.assert_called_once()
        docker_client.containers.run.assert_not_called()
