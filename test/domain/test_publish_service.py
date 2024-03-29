import unittest
import mock

from cpm.domain.project.project_descriptor import ProjectDescriptor
from cpm.domain.publish_service import PublishService
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.project_packager import PackagingFailure
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure


class TestPublishService(unittest.TestCase):
    @mock.patch('cpm.domain.publish_service.project_descriptor_parser')
    def test_publish_service_fails_when_loader_fails_to_load_project(self, project_descriptor_parser):
        project_descriptor_parser.parse_from.side_effect = ProjectDescriptorNotFound
        project_packager = mock.MagicMock()
        cpm_hub_connector = mock.MagicMock()
        service = PublishService(cpm_hub_connector, project_packager=project_packager)

        self.assertRaises(ProjectDescriptorNotFound, service.publish)

    @mock.patch('cpm.domain.publish_service.project_descriptor_parser')
    def test_publish_service_fails_when_packing_project_fails(self, project_descriptor_parser):
        project_descriptor = ProjectDescriptor('cpm-hub')
        project_descriptor_parser.parse_from.return_value = project_descriptor
        project_packager = mock.MagicMock()
        project_packager.pack.side_effect = PackagingFailure
        cpm_hub_connector = mock.MagicMock()
        service = PublishService(cpm_hub_connector, project_packager=project_packager)

        self.assertRaises(PackagingFailure, service.publish)

        project_packager.pack.assert_called_once_with(project_descriptor, 'dist')

    @mock.patch('cpm.domain.publish_service.project_descriptor_parser')
    def test_publish_service_fails_when_uploading_bit_fails(self, project_descriptor_parser):
        project_descriptor = ProjectDescriptor('cpm-hub')
        project_descriptor_parser.parse_from.return_value = project_descriptor
        project_packager = mock.MagicMock()
        project_packager.pack.return_value = 'packaged_file.zip'
        cpm_hub_connector = mock.MagicMock()
        cpm_hub_connector.publish_bit.side_effect = AuthenticationFailure
        service = PublishService(cpm_hub_connector, project_packager=project_packager)

        self.assertRaises(AuthenticationFailure, service.publish)

        cpm_hub_connector.publish_bit.assert_called_once_with(project_descriptor, 'packaged_file.zip')

    @mock.patch('cpm.domain.publish_service.project_descriptor_parser')
    def test_publish_service_loads_project_then_packages_it_and_uploads_it(self, project_descriptor_parser):
        project_descriptor = ProjectDescriptor('cpm-hub')
        project_descriptor_parser.parse_from.return_value = project_descriptor
        project_packager = mock.MagicMock()
        project_packager.pack.return_value = 'packaged_file.zip'
        cpm_hub_connector = mock.MagicMock()
        service = PublishService(cpm_hub_connector, project_packager=project_packager)

        service.publish()

        project_packager.pack.assert_called_once_with(project_descriptor, 'dist')
        cpm_hub_connector.publish_bit.assert_called_once_with(project_descriptor, 'packaged_file.zip')
