import unittest
import mock

from cpm.api.build import build_project
from cpm.domain.project.project_loader import InvalidTarget
from cpm.domain.project_commands import DockerImageNotFound, BuildError
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound, ParseError


class TestApiBuild(unittest.TestCase):
    def test_build_fails_when_current_directory_is_not_a_cpm_project(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.build.side_effect = ProjectDescriptorNotFound()

        result = build_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_fails_when_descriptor_contains_errors(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.build.side_effect = ParseError('project.yaml', 1, 1, 'error')

        result = build_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_fails_when_compilation_fails(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.build.side_effect = BuildError()

        result = build_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_fails_when_target_is_unknown(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.build.side_effect = InvalidTarget()

        result = build_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_fails_when_docker_image_is_not_found(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.build.side_effect = DockerImageNotFound('')

        result = build_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_project_for_host(self):
        compilation_service = mock.MagicMock()
        recipe = mock.MagicMock()

        result = build_project(compilation_service, recipe)

        assert result.status_code == 0
        compilation_service.build.assert_called_once_with(recipe)

    def test_build_project_for_target(self):
        compilation_service = mock.MagicMock()

        result = build_project(compilation_service, target='raspberrypi4:64')

        assert result.status_code == 0
        compilation_service.build.assert_called_once_with('raspberrypi4:64')
