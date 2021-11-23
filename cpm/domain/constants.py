PROJECT_DESCRIPTOR_FILE = 'project.yaml'
BUILD_DIRECTORY = 'build'
CMAKELISTS = 'CMakeLists.txt'
CMAKE_COMMAND = 'cmake'
NINJA_COMMAND = 'ninja'
INITIAL_PROJECT_VERSION = '0.1.0'
DEFAULT_TARGET = 'default'


def bit_directory(name, version):
    return f'bits/{name}/{version}'
