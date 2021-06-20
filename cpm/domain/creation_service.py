from dataclasses import dataclass

from cpm.domain.template_installer import TemplateInstaller
from cpm.infrastructure import filesystem
from cpm.domain.project.project import Project
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.project import project_descriptor_editor
from cpm.domain.project.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.domain.sample_code import CPP_HELLO_WORLD
from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE, INITIAL_PROJECT_VERSION


@dataclass
class CreationOptions:
    project_name: str = 'ProjectName'
    directory: str = '.'
    repository_url: str = 'https://repo.cpmbits.com:8000'
    init_from_existing_sources: bool = False
    generate_sample_code: bool = True
    init_from_template: bool = False
    template_name: str = ''
    template_version: str = 'latest'


class CreationService:
    def __init__(self, project_loader=ProjectLoader(), cpm_hub_connector=CpmHubConnectorV1(), template_installer=TemplateInstaller()):
        self.template_installer = template_installer
        self.project_loader = project_loader
        self.cpm_hub_connector = cpm_hub_connector

    def exists(self, directory):
        try:
            self.project_loader.load(directory)
            return True
        except ProjectDescriptorNotFound:
            return False

    def create(self, options):
        if options.init_from_template:
            return self.__create_from_template(options)
        elif options.init_from_existing_sources:
            return self.__create_from_existing_sources(options)
        else:
            return self.__create_from_scratch(options)

    def __create_from_template(self, options):
        template_download = self.cpm_hub_connector.download_template(options.template_name, options.template_version)
        self.template_installer.install(template_download, options.directory)
        project = self.project_loader.load(options.directory)
        project_descriptor_editor.update(
            options.directory,
            project.descriptor,
            {
                'name': options.project_name,
                'version': INITIAL_PROJECT_VERSION,
            }
        )
        return project

    def __create_from_existing_sources(self, options):
        project = Project(options.project_name)
        self.create_project_descriptor_file(options)
        if options.generate_sample_code:
            self.generate_sample_code(project)
        return project

    def __create_from_scratch(self, options):
        project = Project(options.project_name)

        self.create_project_directory(options.directory)
        filesystem.create_directory(f'{options.directory}/tests')
        self.create_project_descriptor_file(options)
        if options.generate_sample_code:
            self.generate_sample_code(project)
        return project

    def generate_sample_code(self, project):
        filesystem.create_file(
            f'{project.name}/main.cpp',
            CPP_HELLO_WORLD
        )

    def create_project_descriptor_file(self, options):
        filesystem.create_file(
            f"{options.directory}/{PROJECT_DESCRIPTOR_FILE}",
            f"name: '{options.project_name}'\n"
            f"version: {INITIAL_PROJECT_VERSION}\n"
            f"build:\n"
            f"  packages:\n"
            f"  bits:\n"
            f"test:\n"
            f"  bits:\n"
            f"targets:\n"
            f"  default:\n"
            f"    main: 'main.cpp'\n"
        )

    def create_project_directory(self, project_name):
        filesystem.create_directory(project_name)
