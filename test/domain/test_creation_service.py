import unittest
import mock

from cpm.domain.constants import INITIAL_PROJECT_VERSION, PROJECT_DESCRIPTOR_FILE
from cpm.domain.project.project import Project
from cpm.domain.project.project_template import ProjectTemplate
from cpm.domain.sample_code import CPP_HELLO_WORLD
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound


class TestCreationService(unittest.TestCase):
    def test_it_instantiation(self):
        project_loader = mock.MagicMock()
        CreationService(project_loader)

    def test_project_exists_when_loading_the_project_succeeds(self):
        project_loader = mock.MagicMock()
        project_loader.load.return_value = Project('dummy')
        creation_service = CreationService(project_loader)
        directory = '.'

        assert creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    def test_project_does_not_exist_when_loading_the_project_fails(self):
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = ProjectDescriptorNotFound
        creation_service = CreationService(project_loader)
        directory = 'project_location'

        assert not creation_service.exists(directory)
        project_loader.load.assert_called_once_with(directory)

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_it_creates_directory_and_descriptor_file_when_creating_project(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            generate_sample_code=False,
            directory='AwesomeProject',
            project_name='AwesomeProject'
        )

        creation_service.create(creation_options)

        filesystem.create_directory.assert_has_calls([
            mock.call('AwesomeProject'),
            mock.call('AwesomeProject/tests')
        ])
        filesystem.create_file.assert_called_once_with(
            'AwesomeProject/project.yaml',
            mock.ANY
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_it_only_creates_descriptor_file_when_creating_project_from_existing_sources(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            generate_sample_code=False,
            directory='.',
            project_name='AwesomeProject',
            init_from_existing_sources=True
        )

        creation_service.create(creation_options)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_called_once_with(
            './project.yaml',
            mock.ANY
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_creation_service_generates_default_sample_code_when_selected(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            directory='AwesomeProject',
            project_name='AwesomeProject'
        )

        creation_service.create(creation_options)

        filesystem.create_file.assert_called_with(
            'AwesomeProject/main.cpp',
            CPP_HELLO_WORLD
        )

    @mock.patch('cpm.domain.creation_service.filesystem')
    def test_creation_service_returns_generated_project(self, filesystem):
        project_loader = mock.MagicMock()
        creation_service = CreationService(project_loader)
        creation_options = CreationOptions(
            project_name='AwesomeProject'
        )

        project = creation_service.create(creation_options)

        assert project.name == 'AwesomeProject'

    @mock.patch('cpm.domain.creation_service.project_descriptor_editor')
    def test_creation_service_uses_cpm_hub_connector_to_download_template(self, project_descriptor_editor):
        project_loader = mock.MagicMock()
        cpm_hub_connector = mock.MagicMock()
        template_installer = mock.MagicMock()
        creation_service = CreationService(project_loader, cpm_hub_connector, template_installer)
        options = CreationOptions(
            project_name='AwesomeProject',
            init_from_template=True,
            template_name='arduino-uno',
        )
        template_project = Project(name=options.project_name, version=INITIAL_PROJECT_VERSION)
        project_loader.load.return_value = template_project
        project_template = ProjectTemplate(
            name='arduino-uno',
            version='1.0.0',
            payload='payload'
        )
        cpm_hub_connector.download_template.return_value = project_template

        project = creation_service.create(options)

        assert project.name == 'AwesomeProject'
        template_installer.install.assert_called_once_with(project_template, options.directory)
        project_descriptor_editor.update.assert_called_once()

