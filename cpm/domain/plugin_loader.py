from cpm.domain.plugin import Plugin


class PluginLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, plugin, version):
        description = self.yaml_handler.load(f'plugins/{plugin}/plugin.yaml')
        return Plugin(plugin, description)

    def plugin_sources(self, plugin):
        return self.all_sources(f'plugins/{plugin}/sources')

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')
