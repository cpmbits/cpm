from cpm.domain.project_loader import project_descriptor_parser, project_composer

PROJECT_DESCRIPTOR_FILE = 'project.yaml'


class ProjectLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, directory):
        project_description = self.parse_project_descriptor(directory)
        self.parse_build_bit_descriptors(project_description.build.bits,
                                         project_description.build.declared_bits,
                                         lambda description: description.build.declared_bits)
        self.parse_build_bit_descriptors(project_description.test.bits,
                                         project_description.test.declared_bits,
                                         lambda description: description.test.declared_bits)
        return project_composer.compose(project_description, self.filesystem)

    def parse_project_descriptor(self, directory):
        yaml_load = self.yaml_handler.load(f'{directory}/{PROJECT_DESCRIPTOR_FILE}')
        return project_descriptor_parser.parse(yaml_load)

    def parse_build_bit_descriptors(self, bits, declared_bits, next_declared_bits):
        for declared_bit in declared_bits:
            if declared_bit.name not in bits:
                bit_description = self.parse_project_descriptor(f'bits/{declared_bit.name}')
                bits[declared_bit.name] = bit_description
                self.parse_build_bit_descriptors(bits, next_declared_bits(bit_description), next_declared_bits)


class NotACpmProject(RuntimeError):
    pass
