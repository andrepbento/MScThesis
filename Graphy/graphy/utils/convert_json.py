import json
import logging
import os
import sys
from os.path import join

logger = logging.getLogger(__name__)


def is_json(file_path):
    return file_path.endswith('.json')


def convert_json(json_file_path, limit=None):
    """ Converts a JSONL file to JSON """
    logger.info('convert_json()')

    if is_json(json_file_path):
        return json_file_path

    with open(json_file_path) as fp:
        lines = fp.readlines()

    lines = list(
        map(
            lambda x: json.loads(x.strip()),
            lines
        )
    )

    if limit:
        lines = lines[:limit]

    json_array = json.dumps(lines)

    dir_path = os.path.dirname(os.path.realpath(json_file_path))
    file_name = os.path.splitext(json_file_path)[0]
    new_abs_file_path = join(dir_path, file_name + '.json')

    with open(new_abs_file_path, 'w') as f:
        f.write(json_array)

    return new_abs_file_path


# TODO: the following lines are only for testing purposes [REMOVE]
def main():
    if len(sys.argv) != 2:
        print('convert_json.py JSONL_FILE')
        sys.exit(1)
    convert_json(sys.argv[1], 100)


if __name__ == '__main__':
    main()
