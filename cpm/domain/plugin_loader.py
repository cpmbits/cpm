from cpm.domain.plugin import Plugin
from cpm.domain.project import Package


class PluginLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, name):
        return self.load_from(f'plugins/{name}')

    def load_from(self, directory):
        description = self.yaml_handler.load(f'{directory}/plugin.yaml')
        plugin = Plugin(description['name'])
        plugin.version = description.get('version', "0.1")
        for package in self.plugin_packages(description, directory):
            plugin.add_package(package)
            plugin.add_include_directory(self.filesystem.parent_directory(package.path))
            plugin.add_sources(package.sources)
        return plugin

    def plugin_packages(self, description, plugin_path):
        for package in description.get('packages', []):
            yield self._load_package(package, description['packages'][package], plugin_path)
        return []

    def _load_package(self, package, package_description, plugin_path):
        cflags = package_description.get('cflags', []) if package_description is not None else []
        package_path = f'{plugin_path}/{package}'
        sources = self.all_sources(package_path)
        return Package(package_path, sources=sources, cflags=cflags)

    def plugin_sources(self, packages):
        return [source for package in packages for source in self.all_sources(package.path)]

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')
