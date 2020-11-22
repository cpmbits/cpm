import unittest
import mock

from cpm.domain import project_loader
from cpm.domain.project.project_description import ProjectDescription, DeclaredBit


class TestProjectLoader(unittest.TestCase):
    @mock.patch('cpm.domain.project_loader.project_descriptor_parser')
    @mock.patch('cpm.domain.project_loader.project_composer')
    def test_project_loader_without_bits(self, project_composer, project_descriptor_parser):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        # Given
        yaml_handler.load.return_value = 'yaml_load'
        project_descriptor_parser.parse.return_value = ProjectDescription()
        loader = project_loader.ProjectLoader(yaml_handler, filesystem)
        # When
        loader.load('.')
        # Then
        yaml_handler.load.assert_called_once_with('./project.yaml')
        project_descriptor_parser.parse.assert_called_once_with('yaml_load')
        project_composer.compose.assert_called_once_with(project_descriptor_parser.parse.return_value, filesystem)

    @mock.patch('cpm.domain.project_loader.project_descriptor_parser')
    @mock.patch('cpm.domain.project_loader.project_composer')
    def test_project_loader_with_declared_bits(self, project_composer, project_descriptor_parser):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        # Given
        project_description = ProjectDescription()
        project_description.build.declared_bits = [DeclaredBit('bit', '2.2')]
        project_descriptor_parser.parse.return_value = project_description
        loader = project_loader.ProjectLoader(yaml_handler, filesystem)
        # When
        loader.load('.')
        # Then
        yaml_handler.load.assert_has_calls([
            mock.call('./project.yaml'),
            mock.call('bits/bit/project.yaml')
        ])
        project_composer.compose.assert_called_once_with(project_description, filesystem)

