from cpm.domain.project import project_descriptor_parser
from cpm.infrastructure.cpm_hub_connector_v1 import BitNotFound
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.domain.constants import bit_directory


class InstallService(object):
    def __init__(self, project_loader, bit_installer, cpm_hub_connector):
        self.project_loader = project_loader
        self.cpm_hub_connector = cpm_hub_connector
        self.bit_installer = bit_installer

    def install(self, name, version):
        try:
            if not self.__bit_already_installed(name, version):
                bit_download = self.cpm_hub_connector.download_bit(name, version)
                self.bit_installer.install(bit_download)
                print(f'  {f"{name}:{version}": <20} {"✔": >20}')
        except BitNotFound:
            print(f'  {f"{name}:{version}": <20} {f"✖ bit {name} not found in bits repository": >20}')
        except HttpConnectionError as error:
            print(f'  {f"{name}:{version}": <20} {f"✖ failed to connect to bits repository: {error}": >20}')

    def __bit_already_installed(self, name, version):
        try:
            bit_description = project_descriptor_parser.parse_from(bit_directory(name, version))
            return bit_description.version == version
        except:
            return False

    def _log_install_or_upgrade(self, project_description, name, version):
        installed_bit = next((bit for bit in project_description.build.bits if bit.name == name), None)
        if installed_bit:
            print(f'  {"upgrading" if installed_bit.version < version else "downgrading"} {name}:{installed_bit.version} -> {version}')

    def install_all(self, directory='.'):
        print(f'cpm: updating dependencies')
        self.__install_recursively(directory)
        project_descriptor = project_descriptor_parser.parse_from(directory)
        for declared_bit in project_descriptor.test.declared_bits:
            self.install(declared_bit.name, declared_bit.version)
        print(f'cpm: everything up to date')

    def __install_recursively(self, directory='.'):
        project_descriptor = project_descriptor_parser.parse_from(directory)
        for declared_bit in project_descriptor.build.declared_bits:
            self.install(declared_bit.name, declared_bit.version)
            self.__install_recursively(bit_directory(declared_bit.name, declared_bit.version))
