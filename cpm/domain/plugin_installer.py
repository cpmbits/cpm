import base64


class PluginInstaller(object):
    def __init__(self, filesystem, plugin_loader):
        self.plugin_loader = plugin_loader
        self.filesystem = filesystem

    def install(self, plugin_download):
        plugin_directory = f'plugins/{plugin_download.plugin_name}'
        if self.filesystem.directory_exists(plugin_directory):
            self.filesystem.remove_directory(plugin_directory)
        self.filesystem.create_directory(plugin_directory)
        self.filesystem.unzips(base64.b64decode(plugin_download.payload), plugin_directory)

        return self.plugin_loader.load(plugin_download.plugin_name, plugin_download.version)

