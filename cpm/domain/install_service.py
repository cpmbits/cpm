class InstallService(object):
    def __init__(self, project_loader, bit_installer, cpm_hub_connector):
        self.cpm_hub_connector = cpm_hub_connector
        self.project_loader = project_loader
        self.bit_installer = bit_installer

    def install(self, name, version):
        self.project_loader.load()
        print(f'installing {name}:{version}')
        bit_download = self.cpm_hub_connector.download_bit(name, version)
        return self.bit_installer.install(bit_download)

    def install_project_bits(self):
        project = self.project_loader.load()
        for bit_name, version in project.declared_bits.items():
            self.install(bit_name, version)


class BitNotFound(RuntimeError):
    pass
