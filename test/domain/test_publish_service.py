import unittest
from mock import MagicMock

from cpm.domain.project import Project
from cpm.domain.publish_service import PublishService
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.bit_packager import PackagingFailure
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure


class TestPublishService(unittest.TestCase):
    def test_publish_service_fails_when_loader_fails_to_load_project(self):
        project_loader = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        bit_packager = MagicMock()
        cpm_hub_connector = MagicMock()
        service = PublishService(project_loader, bit_packager, cpm_hub_connector)

        self.assertRaises(NotAChromosProject, service.publish)

    def test_publish_service_fails_when_packing_project_fails(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        bit_packager = MagicMock()
        bit_packager.pack.side_effect = PackagingFailure
        cpm_hub_connector = MagicMock()
        service = PublishService(project_loader, bit_packager, cpm_hub_connector)

        self.assertRaises(PackagingFailure, service.publish)

        bit_packager.pack.assert_called_once_with(project, 'dist')

    def test_publish_service_fails_when_uploading_bit_fails(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        bit_packager = MagicMock()
        bit_packager.pack.return_value = 'packaged_file.zip'
        cpm_hub_connector = MagicMock()
        cpm_hub_connector.publish_bit.side_effect = AuthenticationFailure
        service = PublishService(project_loader, bit_packager, cpm_hub_connector)

        self.assertRaises(AuthenticationFailure, service.publish)

        cpm_hub_connector.publish_bit.assert_called_once_with(project, 'packaged_file.zip')

    def test_publish_service_loads_project_then_packages_it_and_uploads_it(self):
        project = Project('cpm-hub')
        project_loader = MagicMock()
        project_loader.load.return_value = project
        bit_packager = MagicMock()
        bit_packager.pack.return_value = 'packaged_file.zip'
        cpm_hub_connector = MagicMock()
        service = PublishService(project_loader, bit_packager, cpm_hub_connector)

        service.publish()

        bit_packager.pack.assert_called_once_with(project, 'dist')
        cpm_hub_connector.publish_bit.assert_called_once_with(project, 'packaged_file.zip')
