import base64

from cpm.infrastructure import filesystem


class BitInstaller(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def install(self, bit_download):
        bit_directory = f'bits/{bit_download.bit_name}'
        if filesystem.directory_exists(bit_directory):
            filesystem.remove_directory(bit_directory)
        filesystem.create_directory(bit_directory)
        filesystem.unzips(base64.b64decode(bit_download.payload), bit_directory)
