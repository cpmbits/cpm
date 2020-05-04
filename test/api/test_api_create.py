import unittest
import mock

from cpm.api.create import new_project
from cpm.domain.creation_service import CreationOptions


class TestApiCreate(unittest.TestCase):
    def test_create_project_uses_creation_service_for_initializing_project(self):
        creation_service = mock.MagicMock()
        creation_service.exists.return_value = False
        options = CreationOptions(
            project_name='Awesome Project'
        )

        result = new_project(creation_service, options)

        assert result.status_code == 0
        creation_service.create.assert_called_once_with(options)

    def test_returns_error_code_when_project_already_exists(self):
        creation_service = mock.MagicMock()
        creation_service.exists.return_value = True
        options = CreationOptions(
            project_name='Awesome Project'
        )

        result = new_project(creation_service, options)

        assert result.status_code == 1

    def test_create_project_accepts_options_from_api(self):
        creation_service = mock.MagicMock()
        creation_service.exists.return_value = False
        options = CreationOptions(
            project_name='Awesome Project',
            generate_sample_code=True
        )

        result = new_project(creation_service, options)

        assert result.status_code == 0
        creation_service.create.assert_called_once_with(options)
