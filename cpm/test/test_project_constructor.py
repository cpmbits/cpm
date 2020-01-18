import unittest
import mock

from cpm.domain.project_constructor import ProjectConstructor


class TestProjectConstructor(unittest.TestCase):
    def test_project_constructor_instantiation(self):
        filesystem = mock.MagicMock()
        project_constructor = ProjectConstructor(filesystem)

    def test_project_constructor_verifies_if_project_exists(self):
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = True
        project_constructor = ProjectConstructor(filesystem)

        assert project_constructor.exists('some project')

    def test_project_constructor_creates_directory_and_descriptor_file_when_creating_project(self):
        filesystem = mock.MagicMock()
        project_constructor = ProjectConstructor(filesystem)

        project_constructor.create('AwesomeProject')

        filesystem.create_directory.assert_called_once_with('AwesomeProject')
        filesystem.create_file.assert_called_once_with(
            'AwesomeProject/project.yaml',
            'project_name: AwesomeProject\n'
        )
