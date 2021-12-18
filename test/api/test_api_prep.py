import unittest
import mock

from cpm.api.prep import prep_project
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound, ParseError


class TestApiUpdate(unittest.TestCase):
    def test_update_fails_when_current_directory_is_not_a_cpm_project(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.update.side_effect = ProjectDescriptorNotFound()

        result = prep_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.update.assert_called_once()

    def test_build_fails_when_descriptor_contains_errors(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.update.side_effect = ParseError('project.yaml', 1, 1, 'error')

        result = prep_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.update.assert_called_once()

    def test_update_project(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()

        result = prep_project(compilation_service, recipe)

        assert result.status_code == 0
        compilation_service.update.assert_called_once()
