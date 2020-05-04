import unittest
import mock

from cpm.api.init import init_project
from cpm.domain.creation_service import CreationOptions


class TestApiInit(unittest.TestCase):
    def test_init_project_uses_creation_service_for_initializing_project(self):
        creation_service = mock.MagicMock()
        creation_service.exists.return_value = False
        options = CreationOptions(
            init_from_existing_sources=True,
            directory='.',
            project_name='Awesome Project'
        )

        result = init_project(creation_service, options)

        assert result.status_code == 0
        creation_service.create.assert_called_once_with(options)

    def test_returns_error_code_when_project_already_exists(self):
        creation_service = mock.MagicMock()
        creation_service.exists.return_value = True

        result = init_project(creation_service)

        assert result.status_code == 1
