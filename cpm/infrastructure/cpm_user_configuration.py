GLOBAL_CONFIGURATION_FILENAME = '.cpm.yaml'
DEFAULT_CONFIGURATION = {
    'cpm_hub_url': 'https://repo.cpmbits.com:8000',
}


class CpmUserConfiguration(object):
    def __init__(self, yaml_handler, filesystem):
        self.yaml_handler = yaml_handler
        self.filesystem = filesystem
        self.global_configuration_file = f'{self.filesystem.home_directory()}/{GLOBAL_CONFIGURATION_FILENAME}'
        self.configuration = DEFAULT_CONFIGURATION.copy()

    def load(self):
        if self.filesystem.file_exists(self.global_configuration_file):
            configuration = self.yaml_handler.load(self.global_configuration_file)
            self.configuration.update(configuration)

    def __getitem__(self, item):
        return self.configuration.get(item, '')
