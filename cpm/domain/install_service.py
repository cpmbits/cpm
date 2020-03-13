class InstallService(object):
    def __init__(self, project_loader, plugin_installer, cpm_hub_connector):
        self.cpm_hub_connector = cpm_hub_connector
        self.project_loader = project_loader
        self.plugin_installer = plugin_installer

    def install(self, plugin_name):
        project = self.project_loader.load()
        plugin_download = self.cpm_hub_connector.download_plugin(plugin_name)
        self.plugin_installer.install(plugin_download)
        project.add_plugin(plugin_download.plugin)
        self.project_loader.save(project)


class PluginNotFound(RuntimeError):
    pass
