class PublishService(object):
    def __init__(self, project_loader, plugin_packager, cpm_hub_connector):
        self.project_loader = project_loader
        self.plugin_packager = plugin_packager
        self.cpm_hub_connector = cpm_hub_connector

    def publish(self):
        project = self.project_loader.load()
        package_name = self.plugin_packager.pack(project, 'dist')
        self.cpm_hub_connector.publish_plugin(project, package_name)
