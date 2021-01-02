from cpm.domain.project import project_descriptor_parser, project_composer


class ProjectLoader(object):
    def load(self, directory):
        project_descriptor = project_descriptor_parser.parse_from(directory)
        # TODO: Target specific bits
        self.parse_build_bit_descriptors(project_descriptor.build.bits,
                                         project_descriptor.build.declared_bits,
                                         lambda description: description.build.declared_bits)
        self.parse_build_bit_descriptors(project_descriptor.test.bits,
                                         project_descriptor.test.declared_bits,
                                         lambda description: description.test.declared_bits)
        return project_composer.compose(project_descriptor)

    def parse_build_bit_descriptors(self, bits, declared_bits, next_declared_bits):
        for declared_bit in declared_bits:
            if declared_bit.name not in bits:
                bit_descriptor = project_descriptor_parser.parse_from(f'bits/{declared_bit.name}')
                bits[declared_bit.name] = bit_descriptor
                self.parse_build_bit_descriptors(bits, next_declared_bits(bit_descriptor), next_declared_bits)
