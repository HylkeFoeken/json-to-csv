import argparse
import sys
import json
import csv
from typing import IO
from io import StringIO


def _parse_args():
    parser = argparse.ArgumentParser(description='Convert list of json objects to csv')
    parser.add_argument('infile', nargs='?', type=str, default='-', help='Input file, defaults to STDIN')
    parser.add_argument('outfile', nargs='?', type=str, default='-', help='Output file, defaults to STDOUT')

    return parser.parse_args()


def _deserialize_json(json_input_file):
    json_data = []
    json_keys = set()

    for line in json_input_file:
        json_object = json.loads(line)
        for key in json_object.keys():
            json_keys.add(key)
        json_data.append(json_object)

    title = list(json_keys)
    return json_data, title


def _serialize_csv(output_csv_file: IO, _header: list, _data: list) -> None:
    cw = csv.DictWriter(output_csv_file, _header)
    cw.writeheader()
    cw.writerows(_data)


def open_filename_arg(filename: str, mode: str, newline: str):
    # the special argument "-" means sys.std{in,out}
    if filename == '-' or filename is None:
        if 'r' in mode:
            return sys.stdin
        elif 'w' in mode:
            return sys.stdout
        else:
            msg = 'argument "-" with mode %r' % mode
            raise ValueError(msg)

    # all other arguments are used as file names
    try:
        return open(filename, mode=mode, newline=newline)
    except OSError as e:
        args = {'filename': filename, 'error': e}
        message = "can't open '%(filename)s': %(error)s"
        raise argparse.ArgumentTypeError(message % args)


def main():
    # lees de argumenten uit de aanroep
    args = _parse_args()

    # deserialiseer python objecten uit json regels
    with open_filename_arg(args.infile, mode='rt', newline='') as infile:
        data, header = _deserialize_json(infile)

    # serialiseer de python objecten als csv bestand
    with open_filename_arg(args.outfile, mode='w', newline='') as outfile:
        _serialize_csv(outfile, header, data)


if __name__ == '__main__':
    main()
