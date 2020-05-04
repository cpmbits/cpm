import unittest
import mock

from cpm.domain.project import Project
from cpm.domain.sample_code import CPP_HELLO_WORLD
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project_loader import NotAChromosProject


class TestCreationService(unittest.TestCase):
    def test_it_instantiation(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        CreationService(filesystem, project_loader)

    def test_project_exists_when_loading_the_project_succeeds(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.return_value = Project('dummy')
        creation_service = CreationService(filesystem, project_loader)
        directory = '.'

        assert creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    def test_project_does_not_exist_when_loading_the_project_fails(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        creation_service = CreationService(filesystem, project_loader)
        directory = 'project_location'

        assert not creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    def test_it_creates_directory_and_descriptor_file_when_creating_project(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        creation_service = CreationService(filesystem, project_loader)

        creation_service.create('AwesomeProject', CreationOptions(generate_sample_code=False))

        filesystem.create_directory.assert_called_once_with('AwesomeProject')
        filesystem.create_file.assert_called_once_with(
            'AwesomeProject/project.yaml',
            'name: AwesomeProject\n'
        )
        
    def test_creation_service_generates_default_sample_code_when_selected(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        creation_service = CreationService(filesystem, project_loader)

        creation_service.create('AwesomeProject')

        filesystem.create_file.assert_called_with(
            'AwesomeProject/main.cpp',
            CPP_HELLO_WORLD
        )

    def test_creation_service_returns_generated_project(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        creation_service = CreationService(filesystem, project_loader)

        project = creation_service.create('AwesomeProject', CreationOptions(generate_sample_code=True))

        assert project.name == 'AwesomeProject'
        assert project.sources == ['main.cpp']

