import unittest
import mock

from cpm.api import create
from cpm.domain import creation_service


class TestInitApi(unittest.TestCase):
    def test_create_project_uses_project_constructor_to_start_project(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = False

        result = create.new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 0
        project_constructor.create.assert_called_once_with('Awesome Project', creation_service.CreationOptions())

    def test_returns_error_code_when_project_already_exists(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = True

        result = create.new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 1

    def test_create_project_accepts_options_from_api(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = False
        options = creation_service.CreationOptions(include_sample_code=True)

        result = create.new_project(project_constructor, 'Awesome Project', options)

        assert result.status_code == 0
        project_constructor.create.assert_called_once_with('Awesome Project', options)
