import base64

from cpm.infrastructure import filesystem


class TemplateInstaller:
    def install(self, template_download, directory):
        if filesystem.directory_exists(directory):
            raise UnableToInstallTemplate
        filesystem.create_directory(directory)
        filesystem.unzips(base64.b64decode(template_download.payload), directory)


class UnableToInstallTemplate(RuntimeError):
    pass
