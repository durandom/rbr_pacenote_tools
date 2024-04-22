#!/usr/bin/env python3

import argparse
import csv
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='split files by category')
    parser.add_argument('file', type=str, help='file')
    args = parser.parse_args()

    notes = []
    categories = set()
    with open(args.file, 'r') as f:
        reader = csv.DictReader(f)
        for note in reader:
            notes.append(note)
            categories.add(note['category'])

    (name, ext) = args.file.split('.')
    for category in categories:
        with open(f'{name}-{category}.csv', 'w') as f:
            csv_writer = csv.DictWriter(f, notes[0].keys())
            csv_writer.writeheader()
            for note in notes:
                if note['category'] == category:
                    csv_writer.writerow(note)

