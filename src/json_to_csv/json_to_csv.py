import argparse
import sys
import json
import csv
from typing import IO


def _parse_args():
    parser = argparse.ArgumentParser(description='Convert list of json objects to csv')
    parser.add_argument('infile', nargs='?', type=str, default='-', help='Input file, defaults to STDIN')
    parser.add_argument('outfile', nargs='?', type=str, default='-', help='Output file, defaults to STDOUT')
    parser.add_argument('-i', '--include', nargs='*', default=set(), help='Include fields, defaults to all')
    parser.add_argument('-e', '--exclude', nargs='*', default=set(), help='Exclude fields, defaults to none')
    parser.add_argument('-o', '--order', nargs='*', default=[], help='Order fields, defaults to none')
    parser.add_argument('-n', '--number', nargs='?', default=-1, help='Number of records to process, defaults to all')
    return parser.parse_args()


def _deserialize_json(json_input_file: IO, max_number_of_records: int):
    line_count = 0
    json_data = []
    json_keys = set()

    for line in json_input_file:
        if max_number_of_records > -1:
            if line_count >= max_number_of_records:
                break

        json_object = json.loads(line)
        for key in json_object.keys():
            json_keys.add(key)
        json_data.append(json_object)
        line_count += 1

    return json_data, json_keys


def _serialize_csv(output_csv_file: IO, _header: list, _data: list) -> None:
    cw = csv.DictWriter(output_csv_file, _header, extrasaction='ignore')
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


def include_fields(fields: set, include_list: set):
    if not include_list:
        return fields  # include all fields by default
    else:
        return fields & include_list


def exclude_fields(fields: set, exclude_list: set):
    if exclude_list:  # do not exclude fields by default
        fields = fields - exclude_list

    return fields


def order_fields(header: set, order_list: list):
    ordered_header_part = [h for h in order_list if h in header]
    unordered_header_part = header - set(ordered_header_part)
    return ordered_header_part + list(unordered_header_part)


def main():
    # lees de argumenten uit de aanroep
    args = _parse_args()

    # deserialiseer python objecten uit json regels
    with open_filename_arg(args.infile, mode='rt', newline='') as infile:
        data, header = _deserialize_json(infile, int(args.number))

    # include fields
    header = include_fields(header, set(args.include))

    # exclude fields
    header = exclude_fields(header, set(args.exclude))

    # order fields
    header = order_fields(header, args.order)

    # serialiseer de python objecten als csv bestand
    with open_filename_arg(args.outfile, mode='w', newline='') as outfile:
        _serialize_csv(outfile, list(header), data)


if __name__ == '__main__':
    main()
