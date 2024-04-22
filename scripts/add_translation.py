#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add translation to pacenotes')
    parser.add_argument('--infiles', nargs='+', help='infiles')
    parser.add_argument('--translation', type=str, help='file with translation')
    args = parser.parse_args()

    translation = []
    with open(args.translation, 'r') as f:
        reader = csv.DictReader(f)
        for note in reader:
            translation.append(note)

    for infile in args.infiles:
        notes = []
        with open(infile, 'r') as f:
            reader = csv.DictReader(f)
            for note in reader:
                notes.append(note)

        keys = list(notes[0].keys())
        keys.append('translation-new')

        (name, ext) = infile.split('.')
        with open(f'{name}-trans.csv', 'w') as f:
            csv_writer = csv.DictWriter(f, fieldnames=keys)
            csv_writer.writeheader()
            for note in notes:
                # find translation
                new_translation = ''
                for t in translation:
                    if t['name'] == note['name']:
                        new_translation = t['translation']
                        break
                note['translation-new'] = new_translation
                csv_writer.writerow(note)
