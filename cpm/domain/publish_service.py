class PublishService(object):
    def __init__(self, project_loader, bit_packager, cpm_hub_connector):
        self.project_loader = project_loader
        self.bit_packager = bit_packager
        self.cpm_hub_connector = cpm_hub_connector

    def publish(self):
        project = self.project_loader.load()
        package_name = self.bit_packager.pack(project, 'dist')
        self.cpm_hub_connector.publish_bit(project, package_name)
