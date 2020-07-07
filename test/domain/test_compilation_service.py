import unittest
from mock import MagicMock
from mock import patch

import os

from cpm.domain.compilation_service import CompilationService, DockerImageNotFound
from cpm.domain.project import Project, Target
from cpm.domain.project_loader import NotAChromosProject


class TestBuildService(unittest.TestCase):
    def test_compilation_service_creation(self):
        project_loader = MagicMock()
        CompilationService(project_loader)

    def test_compilation_service_fails_when_project_loader_fails_to_load_project(self):
        cmake_recipe = MagicMock()
        project_loader = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = CompilationService(project_loader)

        self.assertRaises(NotAChromosProject, service.build, cmake_recipe)
        self.assertRaises(NotAChromosProject, service.update, cmake_recipe)
        project_loader.load.assert_called()

    def test_compilation_service_generates_compilation_recipe_from_project_sources_and_compiles_project(self):
        cmake_recipe = MagicMock()
        project_loader = MagicMock()
        service = CompilationService(project_loader)
        project = Project('ProjectName')
        project_loader.load.return_value = project

        service.build(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.generate.assert_called_once_with(project)
        cmake_recipe.build.assert_called_once_with(project)

    def test_compilation_service_only_generates_compilation_recipe_when_updating(self):
        cmake_recipe = MagicMock()
        project_loader = MagicMock()
        project = Project('ProjectName')
        project_loader.load.return_value = project
        service = CompilationService(project_loader)

        service.update(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.generate.assert_called_once_with(project)

    def test_clean_fails_when_project_loader_fails_to_load_project(self):
        cmake_recipe = MagicMock()
        project_loader = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = CompilationService(project_loader)

        self.assertRaises(NotAChromosProject, service.clean, cmake_recipe)

        project_loader.load.assert_called_once()

    def test_clean_uses_cmake_recipe_to_clean_project(self):
        cmake_recipe = MagicMock()
        project_loader = MagicMock()
        service = CompilationService(project_loader)

        service.clean(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.clean.assert_called_once()

    @patch('cpm.domain.compilation_service.docker')
    def test_it_uses_docker_to_build_for_the_specified_target(self, docker):
        project = Project('Project')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        docker_client = MagicMock()
        container = MagicMock()
        container.logs.return_value = []
        docker_client.containers.return_value = container
        docker.from_env.return_value = docker_client
        service = CompilationService(project_loader)

        service.build_target('raspberrypi4:64')

        project_loader.load.assert_called_once()
        docker_client.containers.run.assert_called_once_with(
            f'cpmbits/raspberrypi4:64',
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )

    @patch('cpm.domain.compilation_service.docker')
    def test_it_uses_image_declared_for_target(self, docker):
        project = Project('Project')
        project.add_target(Target('ubuntu', {'image': 'cpmhub/ubuntu'}))
        project_loader = MagicMock()
        project_loader.load.return_value = project
        docker_client = MagicMock()
        container = MagicMock()
        container.logs.return_value = []
        docker_client.containers.return_value = container
        docker.from_env.return_value = docker_client
        service = CompilationService(project_loader)

        service.build_target('ubuntu')

        project_loader.load.assert_called_once()
        docker_client.containers.run.assert_called_once_with(
            f'cpmhub/ubuntu',
            'cpm build',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )

    @patch('cpm.domain.compilation_service.docker')
    def test_it_raises_an_exception_when_docker_image_is_not_found(self, docker):
        project = Project('Project')
        project.add_target(Target('ubuntu', {'image': 'cpmhub/ubuntu'}))
        project_loader = MagicMock()
        project_loader.load.return_value = project
        docker_client = MagicMock()
        docker.errors.ImageNotFound = RuntimeError
        docker_client.images.pull.side_effect = docker.errors.ImageNotFound
        docker.from_env.return_value = docker_client
        service = CompilationService(project_loader)

        self.assertRaises(DockerImageNotFound, service.build_target, 'ubuntu')

        project_loader.load.assert_called_once()
        docker_client.containers.run.assert_not_called()
