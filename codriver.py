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
            'sounds': 1
        }
        csv_writer = csv.DictWriter(sys.stdout, note.keys())
        csv_writer.writeheader()

        notes = {}
        for pacenote in self.plugin.pacenotes():
            note = {
                'id': pacenote.id(),
                'name': pacenote.name(),
                'translation': self.plugin.translate(pacenote.name()),
                'sounds': pacenote.sounds()
            }
            notes[note['name']] = note

        for note in sorted(notes.values(), key=lambda x: x['name']):
            csv_writer.writerow(note)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # get commandline arguments and parse them
    parser = argparse.ArgumentParser(description='CoDriver')
    parser.add_argument('--codriver', help='Codriver in config.json', default='janne-v3-numeric')
    parser.add_argument('--list-ids', help='List all ids', action='store_true')

    args = parser.parse_args()

    # read the configuration file, which is a json file
    config = json.load(open('config.json'))

    codriver_name = args.codriver
    codriver = CoDriver(config['codrivers'][codriver_name])

    if args.list_ids:
        codriver.list_ids()
