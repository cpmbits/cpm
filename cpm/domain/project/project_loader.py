from cpm.domain.project import project_descriptor_parser, project_composer
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound


class ProjectLoader(object):
    def load(self, directory, target_name='default'):
        project_descriptor = project_descriptor_parser.parse_from(directory)
        if not target_is_valid(project_descriptor, target_name):
            raise InvalidTarget
        # TODO: Target specific bits
        self.parse_bit_build_descriptors(project_descriptor.build.bits,
                                         project_descriptor.build.declared_bits,
                                         lambda description: description.build.declared_bits)
        self.parse_bit_build_descriptors(project_descriptor.test.bits,
                                         project_descriptor.test.declared_bits,
                                         lambda description: description.test.declared_bits)
        return project_composer.compose(project_descriptor, target_name)

    def parse_bit_build_descriptors(self, bits, declared_bits, next_declared_bits):
        for declared_bit in declared_bits:
            if declared_bit.name not in bits:
                try:
                    bit_descriptor = project_descriptor_parser.parse_from(f'bits/{declared_bit.name}')
                    bit_descriptor.declared_bit = declared_bit
                    bits[declared_bit.name] = bit_descriptor
                    self.parse_bit_build_descriptors(bits, next_declared_bits(bit_descriptor), next_declared_bits)
                except ProjectDescriptorNotFound:
                    print(f'cpm: warning: bit \'{declared_bit.name}:{declared_bit.version}\' not installed. '
                          f'Run \'cpm install\' to install missing bits.')


def target_is_valid(project_descriptor, target_name):
    return target_name == 'default' or any(target.name == target_name for target in project_descriptor.targets.values())


class InvalidTarget(RuntimeError):
    pass
