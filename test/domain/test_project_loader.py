import unittest
import mock

from cpm.domain.project import project_loader
from cpm.domain.project.project_descriptor import ProjectDescriptor, DeclaredBit


class TestProjectLoader(unittest.TestCase):
    @mock.patch('cpm.domain.project.project_loader.project_descriptor_parser')
    @mock.patch('cpm.domain.project.project_loader.project_composer')
    def test_project_loader_without_bits(self, project_composer, project_descriptor_parser):
        # Given
        project_descriptor_parser.parse_from.return_value = ProjectDescriptor()
        loader = project_loader.ProjectLoader()
        # When
        loader.load('.')
        # Then
        project_descriptor_parser.parse_from.assert_called_once_with('.')
        project_composer.compose.assert_called_once_with(project_descriptor_parser.parse_from.return_value)

    @mock.patch('cpm.domain.project.project_loader.project_descriptor_parser')
    @mock.patch('cpm.domain.project.project_loader.project_composer')
    def test_project_loader_with_declared_bits(self, project_composer, project_descriptor_parser):
        # Given
        project_descriptor = ProjectDescriptor()
        project_descriptor.build.declared_bits = [DeclaredBit('bit', '2.2')]
        project_descriptor_parser.parse_from.return_value = project_descriptor
        loader = project_loader.ProjectLoader()
        # When
        loader.load('.')
        # Then
        project_descriptor_parser.parse_from.assert_has_calls([
            mock.call('.'),
            mock.call('bits/bit')
        ])
        project_composer.compose.assert_called_once_with(project_descriptor)

