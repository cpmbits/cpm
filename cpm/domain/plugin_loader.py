from cpm.domain.plugin import Plugin


class PluginLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, name, version):
        plugin_path = f'plugins/{name}'
        self.yaml_handler.load(f'{plugin_path}/plugin.yaml')
        plugin = Plugin(name, version)
        plugin.add_include_directory(plugin_path)
        return plugin

    def plugin_sources(self, plugin):
        return self.all_sources(f'plugins/{plugin}/sources')

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')
