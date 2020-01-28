import unittest
import mock

from cpm.domain.sample_code import CPP_HELLO_WORLD
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions


class TestCreationService(unittest.TestCase):
    def test_project_constructor_instantiation(self):
        filesystem = mock.MagicMock()
        CreationService(filesystem)

    def test_project_constructor_verifies_if_project_exists(self):
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = True
        creation_service = CreationService(filesystem)

        assert creation_service.exists('some project')

    def test_project_constructor_creates_directory_and_descriptor_file_when_creating_project(self):
        filesystem = mock.MagicMock()
        creation_service = CreationService(filesystem)

        creation_service.create('AwesomeProject', CreationOptions(generate_sample_code=False))

        filesystem.create_directory.assert_called_once_with('AwesomeProject')
        filesystem.create_file.assert_called_once_with(
            'AwesomeProject/project.yaml',
            'project_name: AwesomeProject\n'
        )
        
    def test_creation_service_generates_default_sample_code_when_selected(self):
        filesystem = mock.MagicMock()
        creation_service = CreationService(filesystem)

        creation_service.create('AwesomeProject')

        filesystem.create_file.assert_called_with(
            'AwesomeProject/main.cpp',
            CPP_HELLO_WORLD
        )

    def test_creation_service_returns_generated_project(self):
        filesystem = mock.MagicMock()
        creation_service = CreationService(filesystem)

        project = creation_service.create('AwesomeProject', CreationOptions(generate_sample_code=True))

        assert project.name == 'AwesomeProject'
        assert project.sources == ['main.cpp']

