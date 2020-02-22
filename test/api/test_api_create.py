import unittest
import mock

from cpm.api.create import new_project
from cpm.domain.creation_service import CreationOptions


class TestApiCreate(unittest.TestCase):
    def test_create_project_uses_creation_service_for_initializing_project(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = False

        result = new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 0
        project_constructor.create.assert_called_once_with('Awesome Project', CreationOptions())

    def test_returns_error_code_when_project_already_exists(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = True

        result = new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 1

    def test_create_project_accepts_options_from_api(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = False
        options = CreationOptions(generate_sample_code=True)

        result = new_project(project_constructor, 'Awesome Project', options)

        assert result.status_code == 0
        project_constructor.create.assert_called_once_with('Awesome Project', options)
