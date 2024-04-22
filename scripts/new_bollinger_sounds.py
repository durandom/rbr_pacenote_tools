#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compose bollinger sounds')
    parser.add_argument('dir', type=str, help='dir')
    args = parser.parse_args()

    notes = [
        ['1', 'plus', '1_plus']
    ]

    # change to the directory
    os.chdir(args.dir)

    for note in notes:
        files = [ f+'.ogg' for f in note]
        command = ['sox'] + files
        logging.info(command)
        subprocess.run(command, check=True)

