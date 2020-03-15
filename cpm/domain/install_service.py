class InstallService(object):
    def __init__(self, project_loader, plugin_installer, cpm_hub_connector):
        self.cpm_hub_connector = cpm_hub_connector
        self.project_loader = project_loader
        self.plugin_installer = plugin_installer

    def install(self, plugin_name):
        self.project_loader.load()
        plugin_download = self.cpm_hub_connector.download_plugin(plugin_name)
        plugin = self.plugin_installer.install(plugin_download)
        self.project_loader.add_plugin(plugin)


class PluginNotFound(RuntimeError):
    pass
