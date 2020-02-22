class PublishService(object):
    def __init__(self, project_loader, plugin_packager, plugin_uploader):
        self.project_loader = project_loader
        self.plugin_packager = plugin_packager
        self.plugin_uploader = plugin_uploader

    def publish(self):
        project = self.project_loader.load()
        package_name = self.plugin_packager.pack(project, 'dist')
        self.plugin_uploader.upload(package_name)
