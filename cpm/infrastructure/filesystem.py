import os
import shutil
from pathlib import Path


class Filesystem:
    def create_directory(self, path):
        os.makedirs(path)

    def create_file(self, name, contents=''):
        with open(name, 'w') as f:
            f.write(contents)

    def directory_exists(self, name):
        return os.path.exists(name) and os.path.isdir(name)

    def parent_directory(self, path):
        return str(Path(path).parent)

    def remove_directory(self, path):
        shutil.rmtree(path)

    def file_exists(self, name):
        return os.path.exists(name) and os.path.isfile(name)

    def find(self, path, pattern):
        return [str(filename) for filename in Path(path).rglob(pattern)]

    def symlink(self, source, destination):
        if Path(destination).is_symlink():
            return
        os.symlink(source, destination, target_is_directory=Path(source).is_dir())
