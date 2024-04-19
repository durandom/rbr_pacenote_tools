#!/usr/bin/env python3

import argparse
import csv
import json
import os
import logging
import sys
from rbr_pacenote_plugin import RbrPacenotePlugin

class CoDriver:
    def list_sounds(self, plugin: RbrPacenotePlugin):
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
        for call, ini_tree in plugin.calls_with_ini_tree():
            note = {
                'id': call.id(),
                'type': call.type(),
                'name': call.name(),
                'translation': plugin.translate(call.name()),
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

    def merge(self, plugin: RbrPacenotePlugin, file, sound_dir=None, language=None):
        plugin.merge_language(language)
        with open(file) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                plugin.merge(row, sound_dir)
        plugin.merge_commit()

    def write(self, out, plugin):
        # check if the directory exists and is empty
        if not os.path.exists(out):
            os.makedirs(out)
        else:
            if len(os.listdir(out)) != 0:
                logging.error(f"Directory {out} is not empty")
                # return

        plugin.write(out)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # get commandline arguments and parse them
    parser = argparse.ArgumentParser(description='CoDriver')
    parser.add_argument('--codriver', help='Codriver in config.json', default='janne-v3-numeric')
    parser.add_argument('--list-sounds', help='List all sounds', action='store_true')
    parser.add_argument('--merge', help='Merge from file', default=None)
    parser.add_argument('--merge-sound-dir', help='Sound dir for merge', default=None)
    parser.add_argument('--merge-language', help='Force new language e.g. english/german/french', default=None)
    parser.add_argument('--out', help='Write to directory', default=None)

    args = parser.parse_args()

    # read the configuration file, which is a json file
    config = json.load(open('config.json'))
    logging.debug(f'package: {config}')
    plugin_config = config['codrivers'][args.codriver]

    plugin = RbrPacenotePlugin(dir=plugin_config['dir'], ini_files=plugin_config['ini'])
    codriver = CoDriver()

    if args.merge:
        dst_plugin = plugin.copy()
        codriver.merge(dst_plugin, args.merge, args.merge_sound_dir, args.merge_language)
        plugin = dst_plugin

    if args.list_sounds:
        codriver.list_sounds(plugin)

    if args.out:
        codriver.write(args.out, plugin)
