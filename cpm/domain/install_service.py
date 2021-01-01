from cpm.domain.project import project_descriptor_parser


class InstallService(object):
    def __init__(self, project_loader, bit_installer, cpm_hub_connector):
        self.project_loader = project_loader
        self.cpm_hub_connector = cpm_hub_connector
        self.bit_installer = bit_installer

    def install(self, name, version):
        if self.__bit_already_installed(name, version):
            print(f'bit already installed: {name}:{version}')
            return
        project_description = project_descriptor_parser.parse_from('.')
        self._log_install_or_upgrade(project_description, name, version)
        bit_download = self.cpm_hub_connector.download_bit(name, version)
        self.bit_installer.install(bit_download)

    def __bit_already_installed(self, name, version):
        try:
            bit_description = project_descriptor_parser.parse_from(f'bits/{name}')
            return bit_description.version == version
        except:
            return False

    def _log_install_or_upgrade(self, project_description, name, version):
        installed_bit = next((bit for bit in project_description.build.bits if bit.name == name), None)
        if installed_bit:
            print(f'{"upgrading" if installed_bit.version < version else "downgrading"} {name}:{installed_bit.version} -> {version}')
        else:
            print(f'installing {name}:{version}')

    def install_all(self, directory='.'):
        self.__install_recursively(directory)
        project_descriptor = project_descriptor_parser.parse_from(directory)
        for declared_bit in project_descriptor.test.declared_bits:
            self.install(declared_bit.name, declared_bit.version)

    def __install_recursively(self, directory='.'):
        project_descriptor = project_descriptor_parser.parse_from(directory)
        for declared_bit in project_descriptor.build.declared_bits:
            self.install(declared_bit.name, declared_bit.version)
            self.__install_recursively(f'bits/{declared_bit.name}')


class BitNotFound(RuntimeError):
    pass
