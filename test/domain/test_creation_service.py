import unittest
import mock

from cpm.domain.project import Project
from cpm.domain.sample_code import CPP_HELLO_WORLD
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project.project_descriptor_parser import NotACpmProject


class TestCreationService(unittest.TestCase):
    def test_it_instantiation(self):
        project_loader = mock.MagicMock()
        CreationService(project_loader)

    def test_project_exists_when_loading_the_project_succeeds(self):
        project_loader = mock.MagicMock()
        project_loader.load.return_value = Project('dummy')
        creation_service = CreationService(project_loader)
        directory = '.'

        assert creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    def test_project_does_not_exist_when_loading_the_project_fails(self):
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotACpmProject
        creation_service = CreationService(project_loader)
        directory = 'project_location'

        assert not creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_it_creates_directory_and_descriptor_file_when_creating_project(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            generate_sample_code=False,
            directory='AwesomeProject',
            project_name='AwesomeProject'
        )

        creation_service.create(creation_options)

        filesystem.create_directory.assert_called_once_with('AwesomeProject')
        filesystem.create_file.assert_called_once_with(
            'AwesomeProject/project.yaml',
            mock.ANY
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_it_only_creates_descriptor_file_when_creating_project_from_existing_sources(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            generate_sample_code=False,
            directory='.',
            project_name='AwesomeProject',
            init_from_existing_sources=True
        )

        creation_service.create(creation_options)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_called_once_with(
            './project.yaml',
            mock.ANY
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_creation_service_generates_default_sample_code_when_selected(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            directory='AwesomeProject',
            project_name='AwesomeProject'
        )

        creation_service.create(creation_options)

        filesystem.create_file.assert_called_with(
            'AwesomeProject/main.cpp',
            CPP_HELLO_WORLD
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_creation_service_returns_generated_project(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            project_name='AwesomeProject'
        )

        project = creation_service.create(creation_options)

        assert project.name == 'AwesomeProject'
        assert project.build.sources == ['main.cpp']

