import json
import sys


def convert_json(jsonl_file):
    """
    Converts a JSONL file to JSON.

    This function fixes the timestamp len issue.
    """
    with open(jsonl_file) as fp:
        lines = fp.readlines()

    lines = list(
        map(
            lambda x: json.loads(x.strip()),
            lines
        )
    )

    lines = lines[:100]

    json_array = json.dumps(lines)

    with open('output.json', 'w') as f:
        f.write(json_array)


def main():
    if len(sys.argv) != 2:
        print('convert_json.py JSONL_FILE')
        sys.exit(1)
    convert_json(sys.argv[1])


if __name__ == '__main__':
    main()
