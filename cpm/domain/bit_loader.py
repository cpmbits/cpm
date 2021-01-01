from cpm.infrastructure import yaml_handler
from cpm.infrastructure import filesystem
from cpm.domain.bit import Bit
from cpm.domain.project import Package


class BitLoader(object):
    def load(self, name):
        return self.load_from(f'bits/{name}')

    def load_from(self, directory):
        description = yaml_handler.load(f'{directory}/bit.yaml')
        bit = Bit(description['name'])
        bit.version = description.get('version', "0.1")
        bit.declared_bits = description.get('bits', {})
        for package in self.bit_packages(description, directory):
            bit.add_package(package)
            bit.add_include_directory(filesystem.parent_directory(package.path))
            bit.add_sources(package.sources)
        return bit

    def bit_packages(self, description, bit_path):
        for package in description.get('packages', []):
            yield self._load_package(package, description['packages'][package], bit_path)
        return []

    def _load_package(self, package, package_description, bit_path):
        cflags = package_description.get('cflags', []) if package_description is not None else []
        package_path = f'{bit_path}/{package}'
        sources = self.all_sources(package_path)
        return Package(package_path, sources=sources, cflags=cflags)

    def bit_sources(self, packages):
        return [source for package in packages for source in self.all_sources(package.path)]

    def all_sources(self, path):
        return filesystem.find(path, '*.cpp') + filesystem.find(path, '*.c')
