import unittest
import mock

from cpm.domain.template_download import TemplateDownload
from cpm.domain.template_installer import TemplateInstaller, UnableToInstallTemplate


class TestTemplateInstaller(unittest.TestCase):
    @mock.patch('cpm.domain.template_installer.filesystem')
    def test_template_installation_when_template_was_not_installed_before(self, filesystem):
        installer = TemplateInstaller()
        template_download = TemplateDownload("arduino", "1.0", "dGVtcGxhdGUgZG93bmxvYWQ=")
        filesystem.directory_exists.return_value = False

        installer.install(template_download, './project')

        filesystem.create_directory.assert_called_once_with('./project')
        filesystem.unzips.assert_called_once_with(b'template download', './project')

    @mock.patch('cpm.domain.template_installer.filesystem')
    def test_template_installation_raises_an_error_when_directory_sxists(self, filesystem):
        installer = TemplateInstaller()
        template_download = TemplateDownload("arduino", "1.0", "dGVtcGxhdGUgZG93bmxvYWQ=")
        filesystem.directory_exists.return_value = True

        self.assertRaises(UnableToInstallTemplate, installer.install, template_download, './project')

