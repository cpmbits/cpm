import unittest
from mock import MagicMock
from mock import call

from cpm.domain.bit_loader import BitLoader
from cpm.domain.project import Package


class TestBitLoader(unittest.TestCase):
    def test_creating_bit_loader(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        BitLoader(yaml_handler, filesystem)

    def test_loading_bit_without_packages(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'name': 'cest'
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load('cest')

        yaml_handler.load.assert_called_once_with('bits/cest/bit.yaml')
        assert bit.name == 'cest'
        assert bit.include_directories == []

    def test_loading_bit_with_given_version(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'name': 'cest',
            'version': '4.7.5',
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load('cest')

        yaml_handler.load.assert_called_once_with('bits/cest/bit.yaml')
        assert bit.name == 'cest'
        assert bit.version == '4.7.5'

    def test_loading_bit_from_directory(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'name': 'cest'
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load_from('bits/cest')

        yaml_handler.load.assert_called_once_with('bits/cest/bit.yaml')
        assert bit.name == 'cest'
        assert bit.include_directories == []

    def test_loading_bit_with_transitive_dependencies(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'name': 'cest',
            'bits': {
                'cest': '1.0'
            }
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load_from('bits/cest')

        yaml_handler.load.assert_called_once_with('bits/cest/bit.yaml')
        assert bit.name == 'cest'
        assert bit.declared_bits == {
            'cest': '1.0'
        }

    def test_loading_bit_with_one_package(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        filesystem.parent_directory.return_value = 'bits/cest'
        filesystem.find.side_effect = [['bits/cest/bit.cpp'], ['bits/cest/bit.c']]
        yaml_handler.load.return_value = {
            'name': 'cest',
            'packages': {'cest': None},
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load('cest')

        assert bit.name == 'cest'
        assert Package(path='bits/cest/cest', sources=['bits/cest/bit.cpp', 'bits/cest/bit.c']) in bit.packages
        assert bit.include_directories == ['bits/cest']
        assert bit.sources == ['bits/cest/bit.cpp', 'bits/cest/bit.c']

    def test_loading_bit_with_one_package_with_cflags(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        filesystem.parent_directory.return_value = 'bits/cest'
        filesystem.find.side_effect = [['bits/cest/bit.cpp'], ['bits/cest/bit.c']]
        yaml_handler.load.return_value = {
            'name': 'cest',
            'packages': {
                'cest': {
                    'cflags': ['-std=c++11']
                }
            },
        }
        loader = BitLoader(yaml_handler, filesystem)

        bit = loader.load('cest')

        assert bit.name == 'cest'
        assert Package(path='bits/cest/cest', sources=['bits/cest/bit.cpp', 'bits/cest/bit.c'], cflags=['-std=c++11']) in bit.packages

    def test_finding_bit_sources(self):
        filesystem = MagicMock()
        filesystem.find.side_effect = [['bits/cest/bit.cpp'], ['bits/cest/bit.c']]
        yaml_handler = MagicMock()
        loader = BitLoader(yaml_handler, filesystem)

        sources = loader.bit_sources([Package('bits/cest')])

        assert sources == ['bits/cest/bit.cpp', 'bits/cest/bit.c']
        filesystem.find.assert_has_calls([
            call('bits/cest', '*.cpp'),
            call('bits/cest', '*.c'),
        ])
