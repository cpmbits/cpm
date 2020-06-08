from cpm.domain.bit import Bit


class InstallService(object):
    def __init__(self, project_loader, bit_installer, cpm_hub_connector):
        self.cpm_hub_connector = cpm_hub_connector
        self.project_loader = project_loader
        self.bit_installer = bit_installer

    def install(self, name, version):
        project = self.project_loader.load()
        if Bit(name, version) in project.bits:
            print(f'bit already installed: {name}:{version}')
            return
        self._log_install_or_upgrade(project, name, version)
        bit_download = self.cpm_hub_connector.download_bit(name, version)
        bit = self.bit_installer.install(bit_download)
        for bit_name, version in bit.declared_bits.items():
            self.install(bit_name, version)

    def _log_install_or_upgrade(self, project, name, version):
        installed_bit = next((bit for bit in project.bits if bit.name == name), None)
        if installed_bit:
            print(f'{"upgrading" if installed_bit.version < version else "downgrading"} {name}:{installed_bit.version} -> {version}')
        else:
            print(f'installing {name}:{version}')

    def install_project_bits(self):
        project = self.project_loader.load()
        for bit_name, version in project.declared_bits.items():
            self.install(bit_name, version)
        for bit_name, version in project.declared_test_bits.items():
            self.install(bit_name, version)


class BitNotFound(RuntimeError):
    pass
