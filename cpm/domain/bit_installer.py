import base64

from cpm.infrastructure import filesystem
from cpm.domain.constants import bit_directory


class BitInstaller(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def install(self, bit_download):
        directory = bit_directory(bit_download.bit_name, bit_download.version)
        if filesystem.directory_exists(directory):
            filesystem.remove_directory(directory)
        filesystem.create_directory(directory)
        filesystem.unzips(base64.b64decode(bit_download.payload), directory)
