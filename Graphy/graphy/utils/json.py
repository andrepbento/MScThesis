import logging
import os
import sys
from os.path import join

from graphy.models.span import fix_timestamps

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger(__name__)


def is_json(file_path):
    return file_path.endswith('.json')


def to_json(file_path, limit=None):
    """
    Converts a file to JSON

    :param file_path: The file path.
    :param limit: Limit the number of entries to convert to the new file.
    :return: The file path of the created file.
    """
    logger.debug('convert_json()')

    if is_json(file_path):
        return file_path

    with open(file_path) as fp:
        lines = fp.readlines()

    lines = list(
        map(
            lambda x: json.loads(x.strip()),
            lines
        )
    )

    if limit:
        lines = lines[:limit]

    fix_timestamps(lines)

    json_array = json.dumps(lines)

    dir_path = os.path.dirname(os.path.realpath(file_path))
    file_name = os.path.splitext(file_path)[0]
    new_abs_file_path = join(dir_path, file_name + '.json')

    with open(new_abs_file_path, 'w') as f:
        f.write(json_array)

    return new_abs_file_path


# TODO: the following lines are only for testing purposes [REMOVE]
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('utils.py JSONL_FILE')
        sys.exit(1)
    print('File created in:', to_json(sys.argv[1], None))
