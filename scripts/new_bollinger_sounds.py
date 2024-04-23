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
        ['1', 'plus', '1_plus'],
        ['sharp', 'left', 'sharp_left'],
        ['sharp', 'right', 'sharp_right'],
        ['six_left', 'plus', 'six_left_plus'],
        ['six_right', 'plus', 'six_right_plus'],
        ['five_left', 'plus', 'five_left_plus'],
        ['five_right', 'plus', 'five_right_plus'],
        ['four_left', 'plus', 'four_left_plus'],
        ['four_right', 'plus', 'four_right_plus'],
        ['three_left', 'plus', 'three_left_plus'],
        ['three_right', 'plus', 'three_right_plus'],
        ['two_left', 'plus', 'two_left_plus'],
        ['two_right', 'plus', 'two_right_plus'],
        ['one_left', 'plus', 'one_left_plus'],
        ['one_right', 'plus', 'one_right_plus'],
        ['hairpin_left', 'plus', 'hairpin_left_plus'],
        ['hairpin_right', 'plus', 'hairpin_right_plus'],
        ['6', 'plus', 'six_plus'],
        ['5', 'plus', 'five_plus'],
        ['4', 'plus', 'four_plus'],
        ['3', 'plus', 'three_plus'],
        ['2', 'plus', 'two_plus'],
        ['1', 'plus', 'one_plus'],
        ['hairpin', 'plus', 'hairpin_plus'],
        ['short', 'left', 'short_left'],
        ['short', 'right', 'short_right'],
        ['left', 'over', 'left_over'],
        ['right', 'over', 'right_over'],
        ['tightens', 'hairpin', 'tightens_hairpin'],
        ['tightens', 'sharp', 'tightens_sharp'],
        ['in', 'sharp', 'in_sharp'],
        ['tightens', 'hard', 'late', 'tightens_hard_late'],
        ['opens', 'light', 'opens_light'],
        ['opens', 'long', 'opens_long'],
        ['opens', 'very_long', 'opens_very_long'],
        ['opens', 'early', 'opens_early'],
        ['opens', 'junction', 'opens_junction'],
        ['opens', 'overcrest', 'opens_overcrest'],
        ['tightens', 'early', 'tightens_early'],
        ['tightens', 'light', 'tightens_light'],
        ['tightens', 'long', 'tightens_long'],
        ['tightens', 'very_long', 'tightens_very_long'],
        ['tightens', 'junction', 'tightens_junction'],
        ['tightens', 'overcrest', 'tightens_overcrest'],
        ['tightens', '6', 'plus', 'tightens_six_plus'],
        ['tightens', '5', 'plus', 'tightens_five_plus'],
        ['tightens', '4', 'plus', 'tightens_four_plus'],
        ['tightens', '3', 'plus', 'tightens_three_plus'],
        ['tightens', '2', 'plus', 'tightens_two_plus'],
        ['tightens', '1', 'plus', 'tightens_one_plus'],
        ['tightens', 'hairpin', 'plus', 'tightens_hairpin_plus'],
        ['in', '6', 'plus', 'in_six_plus'],
        ['in', '5', 'plus', 'in_five_plus'],
        ['in', '4', 'plus', 'in_four_plus'],
        ['in', '3', 'plus', 'in_three_plus'],
        ['in', '2', 'plus', 'in_two_plus'],
        ['in', '1', 'plus', 'in_one_plus'],
        ['in', 'hairpin', 'plus', 'in_hairpin_plus'],



    ]

    # change to the directory
    os.chdir(args.dir)

    for note in notes:
        files = [ f+'.ogg' for f in note]
        command = ['sox'] + files
        logging.info(command)
        subprocess.run(command, check=True)

