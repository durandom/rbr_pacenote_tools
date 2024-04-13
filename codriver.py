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

    def list_ids(self):
        note = {
            'id': 'id',
            'name': 'name',
            'translation': 'translation',
            'file': 'file',
            'sounds': 1,
            'ini': 'ini_file'
        }
        csv_writer = csv.DictWriter(sys.stdout, note.keys())
        csv_writer.writeheader()

        notes = []
        for pacenote, ini_tree in self.plugin.pacenotes(with_ini_tree=True):
            note = {
                'id': pacenote.id(),
                'name': pacenote.name(),
                'translation': self.plugin.translate(pacenote.name()),
                'file': '',
                'sounds': pacenote.sounds(),
                'ini': "/".join([f"{x.dir_name}/{x.file_name}" for x in ini_tree])
            }
            files = pacenote.files()
            if files:
                for file in files:
                    new_note = note.copy()
                    new_note['file'] = file
                    notes.append(new_note)
            else:
                notes.append(note)

        for note in sorted(notes, key=lambda x: [x['id'], x['name']]):
            csv_writer.writerow(note)

    def merge(self, file):
        # open CSV file
        with open(file) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                self.plugin.merge(row)

    def merge_commit(self):
        self.plugin.merge_commit()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # get commandline arguments and parse them
    parser = argparse.ArgumentParser(description='CoDriver')
    parser.add_argument('--codriver', help='Codriver in config.json', default='janne-v3-numeric')
    parser.add_argument('--list-ids', help='List all ids', action='store_true')
    parser.add_argument('--merge', help='Merge from file', default=None)

    args = parser.parse_args()

    # read the configuration file, which is a json file
    config = json.load(open('config.json'))

    codriver_name = args.codriver
    codriver = CoDriver(config['codrivers'][codriver_name])

    if args.merge:
        codriver.merge(args.merge)
        codriver.merge_commit()

    if args.list_ids:
        codriver.list_ids()