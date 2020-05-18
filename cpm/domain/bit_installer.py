import base64


class BitInstaller(object):
    def __init__(self, filesystem, bit_loader):
        self.bit_loader = bit_loader
        self.filesystem = filesystem

    def install(self, bit_download):
        bit_directory = f'bits/{bit_download.bit_name}'
        if self.filesystem.directory_exists(bit_directory):
            self.filesystem.remove_directory(bit_directory)
        self.filesystem.create_directory(bit_directory)
        self.filesystem.unzips(base64.b64decode(bit_download.payload), bit_directory)

        return self.bit_loader.load(bit_download.bit_name)

