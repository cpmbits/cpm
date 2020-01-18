import unittest
import mock

from cpm.api import create


class TestInitApi(unittest.TestCase):
    def test_api_creates_project_uses_project_constructor_to_start_project(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = False

        result = create.new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 0
        project_constructor.create.assert_called_once_with('Awesome Project')

    def test_api_returns_error_code_when_project_already_exists(self):
        project_constructor = mock.MagicMock()
        project_constructor.exists.return_value = True

        result = create.new_project(project_constructor, 'Awesome Project')

        assert result.status_code == 1
