import os
from os.path import dirname, join

ROOT_PROJECT_DIRECTORY = '/'.join(dirname(dirname(__file__)).split('/')[:-1])


def file_exists(relative_path):
    return os.path.isfile(relative_path)


def get_absolute_path(relative_path):
    if relative_path:
        return os.path.abspath(relative_path)
    return ''


def get_root_path(*path):
    return join(ROOT_PROJECT_DIRECTORY, *path)


def get_data_path(*path):
    data_path = join(ROOT_PROJECT_DIRECTORY, 'data')
    r_path = join(data_path, *path)
    return r_path


def read_file(path):
    with open(path) as fp:
        file_data = fp.read()
    return file_data
