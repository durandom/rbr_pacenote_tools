#!/usr/bin/env python3

import argparse
import csv
import json
import os
import logging
import sys
from rbr_pacenote_plugin import RbrPacenotePlugin

class CoDriver:
    def list_sounds(self, plugin: RbrPacenotePlugin, file='', unique=False, fields=''):
        if not file:
            file = sys.stdout
        else:
            file = open(file, 'w')

        note = {
            'id': 'id',
            'type': 'type',
            'category': 'category',
            'name': 'name',
            'translation': 'translation',
            'file': 'file',
            'sounds': 1,
            'error': '',
            'ini': 'ini_file',
            'file_src_dir': '',
        }
        all_fields = list(note.keys())
        if fields:
            fields = fields.split(',')
        else:
            fields = list(note.keys())

        for key in all_fields:
            if key not in fields:
                note.pop(key)

        csv_writer = csv.DictWriter(file, note.keys())
        csv_writer.writeheader()

        notes = []
        for call, ini_tree in plugin.calls_with_ini_tree():
            note = {
                'id': call.id(),
                'type': call.type(),
                'category': call.category(),
                'name': call.name(),
                'translation': plugin.translate(call.name()),
                'file': '',
                'sounds': call.sounds(),
                'file_src_dir': call.get_sound_dir(),
                'error': call.error(),
                'ini': "/".join([f"{x.basename}/{x.filename}" for x in ini_tree])
            }
            files = call.files()
            if files:
                for file in files:
                    new_note = note.copy()
                    new_note['file'] = file
                    new_note['error'] = call.file_error(file)
                    notes.append(new_note)
            else:
                notes.append(note)

        if unique:
            unique_notes = {}
            for note in notes:
                key = f"{note['id']}-{note['type']}-{note['name']}"
                if key not in unique_notes:
                    unique_notes[key] = note
            notes = list(unique_notes.values())

        for note in sorted(notes, key=lambda x: [x['id'], x['name']]):
            for key in all_fields:
                if key not in fields:
                    note.pop(key)
            csv_writer.writerow(note)

    def merge(self, plugin: RbrPacenotePlugin, files = [], sound_dir=None):
        for file in files:
            with open(file) as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    # logging.debug(f"Merge: {row}")
                    if row['file']:
                        base_file = row['file']
                        for index in range(9):
                            file = base_file
                            if not file.endswith('.ogg'):
                                file = file + '.ogg'
                            (basename, ext) = os.path.splitext(file)
                            if index > 0:
                                file = f"{basename}_{index}{ext}"
                            pathname = os.path.join(sound_dir, file)
                            if os.path.exists(pathname):
                                row['file'] = file
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
    parser.add_argument('--list-fields', help='Only list fields', default='id,type,category,name,translation,file,sounds,error,ini,file_src_dir')
    parser.add_argument('--list-sounds', help='List all sounds', default=None)
    parser.add_argument('--list-sounds-unique', help='List all sounds only one', action='store_true')
    parser.add_argument('--merge', help='Merge from file', default=None, nargs='+')
    parser.add_argument('--merge-sound-src-dir', help='Sound dir for merge', default=None)
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
        # dst_plugin = RbrPacenotePlugin(dir=plugin_config['dir'], ini_files=plugin_config['ini'])
        plugin.set_language(args.merge_language)
        codriver.merge(plugin, args.merge, args.merge_sound_src_dir)
        plugin.set_sound_dir(args.merge_sound_dir)

    if args.list_sounds:
        codriver.list_sounds(plugin, args.list_sounds, args.list_sounds_unique, args.list_fields)

    if args.out:
        codriver.write(args.out, plugin)
