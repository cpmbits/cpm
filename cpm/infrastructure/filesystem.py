import os
import shutil
import zipfile
import io
from distutils.dir_util import copy_tree
from pathlib import Path


def create_file(file_name, contents=''):
    with open(file_name, 'w') as f:
        f.write(contents)


def read_file(file_name, mode='r'):
    with open(file_name, mode) as file_stream:
        return file_stream.read()


def file_exists(name):
    return os.path.exists(name) and os.path.isfile(name)


def copy_file(origin, destination):
    shutil.copy2(origin, destination)


def delete_file(file_name):
    os.remove(file_name)


def create_directory(path):
    os.makedirs(path)


def copy_directory(origin, destination):
    copy_tree(origin, destination)


def directory_exists(name):
    return os.path.exists(name) and os.path.isdir(name)


def parent_directory(path):
    return str(Path(path).parent)


def remove_directory(path):
    shutil.rmtree(path)


def list_directories(path):
    if directory_exists(path):
        return next(os.walk(path))[1]
    return []


def home_directory():
    return str(Path.home())


def find(path, pattern):
    return [str(filename) for filename in Path(path).rglob(pattern)]


def zip(directory, output_filename):
    shutil.make_archive(output_filename, 'zip', directory)


def unzips(payload, directory):
    zip = zipfile.ZipFile(io.BytesIO(payload))
    zip.extractall(path=directory)
    zip.close()


def symlink(source, destination):
    if Path(destination).is_symlink():
        return
    os.symlink(source, destination, target_is_directory=Path(source).is_dir())
