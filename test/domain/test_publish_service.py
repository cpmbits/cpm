import unittest
from mock import MagicMock

from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.publish_service import PublishService
from cpm.domain.plugin_packager import PackagingError
from cpm.domain.plugin_uploader import AuthenticationFailure


class TestPublishService(unittest.TestCase):
    def test_publish_service_fails_when_loader_fails_to_load_project(self):
        project_loader = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        plugin_packager = MagicMock()
        plugin_uploader = MagicMock()
        service = PublishService(project_loader, plugin_packager, plugin_uploader)

        self.assertRaises(NotAChromosProject, service.publish)

    def test_publish_service_fails_when_packing_project_fails(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        plugin_packager = MagicMock()
        plugin_packager.pack.side_effect = PackagingError
        plugin_uploader = MagicMock()
        service = PublishService(project_loader, plugin_packager, plugin_uploader)

        self.assertRaises(PackagingError, service.publish)

        plugin_packager.pack.assert_called_once_with(project, 'dist')

    def test_publish_service_fails_when_uploading_plugin_fails(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        plugin_packager = MagicMock()
        plugin_packager.pack.return_value = 'plugin_package'
        plugin_uploader = MagicMock()
        plugin_uploader.upload.side_effect = AuthenticationFailure
        service = PublishService(project_loader, plugin_packager, plugin_uploader)

        self.assertRaises(AuthenticationFailure, service.publish)

        plugin_uploader.upload.assert_called_once_with('plugin_package')

    def test_publish_service_loads_project_then_packages_it_and_uploads_it(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        plugin_packager = MagicMock()
        plugin_packager.pack.return_value = 'plugin_package'
        plugin_uploader = MagicMock()
        service = PublishService(project_loader, plugin_packager, plugin_uploader)

        service.publish()

        plugin_packager.pack.assert_called_once_with(project, 'dist')
        plugin_uploader.upload.assert_called_once_with('plugin_package')
