#!/usr/bin/env python3

import argparse
import csv
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate new ids for pacenotes')
    parser.add_argument('file1', type=str, help='file1')
    parser.add_argument('file2', type=str, help='file2')
    args = parser.parse_args()

    notes1 = {}
    with open(args.file1, 'r') as f:
        reader = csv.DictReader(f)
        for note in reader:
            notes1[note['id']] = note

    notes2 = {}
    with open(args.file2, 'r') as f:
        reader = csv.DictReader(f)
        for note in reader:
            notes2[note['id']] = note

    csv_writer = csv.DictWriter(sys.stdout, fieldnames=notes1['-1'].keys())
    csv_writer.writeheader()
    for id, note in notes2.items():
        if id not in notes1:
            csv_writer.writerow(note)
