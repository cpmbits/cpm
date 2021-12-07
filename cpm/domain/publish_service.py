from cpm.domain.project_packager import ProjectPackager
from cpm.domain.template_packager import TemplatePackager
from cpm.domain.project import project_descriptor_parser


class PublishService(object):
    def __init__(self, cpm_hub_connector, project_packager=ProjectPackager(), template_packager=TemplatePackager()):
        self.template_packager = template_packager
        self.project_packager = project_packager
        self.cpm_hub_connector = cpm_hub_connector

    def publish(self):
        project_descriptor = project_descriptor_parser.parse_from('.')
        package_name = self.project_packager.pack(project_descriptor, 'dist')
        self.cpm_hub_connector.publish_bit(project_descriptor, package_name)

    def publish_template(self):
        project_descriptor = project_descriptor_parser.parse_from('.')
        package_name = self.template_packager.pack(project_descriptor, 'dist')
        self.cpm_hub_connector.publish_template(project_descriptor, package_name)
