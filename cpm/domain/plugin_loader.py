from cpm.domain.plugin import Plugin
from cpm.domain.project import Package


class PluginLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, name, version):
        plugin_path = f'plugins/{name}'
        description = self.yaml_handler.load(f'{plugin_path}/plugin.yaml')
        plugin = Plugin(name, version)
        for package in self.plugin_packages(description, plugin_path):
            plugin.add_package(package)
            plugin.add_include_directory(self.filesystem.parent_directory(package.path))
        plugin.add_sources(self.plugin_sources(plugin.packages))
        return plugin

    def plugin_packages(self, description, plugin_path):
        if 'packages' in description:
            for package in description['packages']:
                yield Package(f'{plugin_path}/{package}')
        return []

    def plugin_sources(self, packages):
        return [source for package in packages for source in self.all_sources(package.path)]

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')
