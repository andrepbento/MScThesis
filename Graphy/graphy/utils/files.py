"""
    Author: André Bento
    Date last modified: 12-02-2019
"""
import os
from os.path import dirname

ROOT_PROJECT_DIRECTORY = os.path.join(dirname(dirname(dirname(__file__))))


class FileException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


def get_absolute_path(relative_path, from_project=False):
    if from_project:
        relative_path = os.path.join(ROOT_PROJECT_DIRECTORY, relative_path)

    abs_path = os.path.abspath(relative_path)

    if os.path.isfile(abs_path) is True and os.path.exists(abs_path):
        return abs_path
    raise FileNotFoundError


def read_file(path):
    with open(path) as fp:
        file_data = fp.read()
    return file_data
