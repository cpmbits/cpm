import os
import shutil
import zipfile
import io
from distutils.dir_util import copy_tree
from pathlib import Path


class Filesystem:
    def create_directory(self, path):
        os.makedirs(path)

    def create_file(self, file_name, contents=''):
        with open(file_name, 'w') as f:
            f.write(contents)

    def read_file(self, file_name, mode='r'):
        with open(file_name, mode) as file_stream:
            return file_stream.read()

    def copy_file(self, origin, destination):
        shutil.copy2(origin, destination)

    def delete_file(self, file_name):
        os.remove(file_name)

    def copy_directory(self, origin, destination):
        copy_tree(origin, destination)

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

    def zip(self, directory, output_filename):
        shutil.make_archive(output_filename, 'zip', directory)

    def unzips(self, payload, directory):
        zip = zipfile.ZipFile(io.BytesIO(payload))
        zip.extractall(path=directory)
        zip.close()

    def symlink(self, source, destination):
        if Path(destination).is_symlink():
            return
        os.symlink(source, destination, target_is_directory=Path(source).is_dir())
