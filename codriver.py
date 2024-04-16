#!/usr/bin/env python3

import argparse
import csv
import json
import os
import logging
import sys
from rbr_pacenote_plugin import RbrPacenotePlugin

class CoDriver:
    def __init__(self, config):
        logging.debug(f'package: {config}')
        self.plugin = RbrPacenotePlugin(dir=config['dir'], ini_files=config['ini'])

    def list_sounds(self):
        note = {
            'id': 'id',
            'type': 'type',
            'name': 'name',
            'translation': 'translation',
            'file': 'file',
            'sounds': 1,
            'ini': 'ini_file'
        }
        csv_writer = csv.DictWriter(sys.stdout, note.keys())
        csv_writer.writeheader()

        notes = []
        for call, ini_tree in self.plugin.calls_with_ini_tree():
            note = {
                'id': call.id(),
                'type': call.type(),
                'name': call.name(),
                'translation': self.plugin.translate(call.name()),
                'file': '',
                'sounds': call.sounds(),
                'ini': "/".join([f"{x.basename}/{x.filename}" for x in ini_tree])
            }
            files = call.files()
            if files:
                for file in files:
                    new_note = note.copy()
                    new_note['file'] = file
                    notes.append(new_note)
            else:
                notes.append(note)

        for note in sorted(notes, key=lambda x: [x['id'], x['name']]):
            csv_writer.writerow(note)

    def merge(self, file, sound_dir=None):
        # open CSV file
        with open(file) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                self.plugin.merge(row, sound_dir)

    def merge_commit(self):
        self.plugin.merge_commit()

    def write(self, out):
        # check if the directory exists and is empty
        if not os.path.exists(out):
            os.makedirs(out)
        else:
            if len(os.listdir(out)) != 0:
                logging.error(f"Directory {out} is not empty")
                # return

        self.plugin.write(out)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # get commandline arguments and parse them
    parser = argparse.ArgumentParser(description='CoDriver')
    parser.add_argument('--codriver', help='Codriver in config.json', default='janne-v3-numeric')
    parser.add_argument('--list-sounds', help='List all sounds', action='store_true')
    parser.add_argument('--merge', help='Merge from file', default=None)
    parser.add_argument('--merge-sound-dir', help='Sound dir for merge', default=None)
    parser.add_argument('--language', help='Force new language e.g. english/german/french', default=None)
    parser.add_argument('--out', help='Write to directory', default=None)

    args = parser.parse_args()

    # read the configuration file, which is a json file
    config = json.load(open('config.json'))

    codriver_name = args.codriver
    codriver = CoDriver(config['codrivers'][codriver_name])

    if args.merge:
        codriver.merge(args.merge, args.merge_sound_dir)
        codriver.merge_commit()

    if args.list_sounds:
        codriver.list_sounds()

    if args.out:
        codriver.write(args.out)
