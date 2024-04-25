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
        ['in', 'hairpin', 'in_hairpin'],
        ['onto', 'finish', 'onto_finish'],
        ['dontcut', 'early', 'dontcut_early'],
        ['dontcut', 'late', 'dontcut_late'],
        ['in', 'dip', 'in_dip'],
        ['jump', 'small' 'jump_small'],
        ['jump', 'big', 'jump_big'],
        ['continuesovercrest', 'small', 'continuesovercrest_small'],
        ['long', 'crest', 'long_crest'],
        ['onto', 'bump', 'onto_bump'],
        ['twisty', 'left', 'twisty_left'],
        ['twisty', 'right', 'twisty_right'],
        ['grip', 'keepmiddle', 'grip_keepmiddle'],
        ['grip', 'inside', 'grip_inside'],
        ['grip', 'outside', 'grip_outside'],
        ['at', 'left', 'at_left'],
        ['at', 'right', 'at_right'],
        ['jump', 'brake', 'jump_brake'],
        ['rock', 'inside', 'rock_inside'],
        ['rock', 'outside', 'rock_outside'],
        ['tree', 'inside', 'tree_inside'],
        ['tree', 'outside', 'tree_outside'],
        ['ditch', 'inside', 'ditch_inside'],
        ['ditch', 'outside', 'ditch_outside'],
        ['house', 'inside', 'house_inside'],
        ['house', 'outside', 'house_outside'],
        ['fence', 'inside', 'fence_inside'],
        ['fence', 'outside', 'fence_outside'],
        ['sign', 'inside', 'sign_inside'],
        ['sign', 'outside', 'sign_outside'],
        ['post', 'inside', 'post_inside'],
        ['post', 'outside', 'post_outside'],
        ['brake', 'into', 'brake_into'],
        ['brake', 'and', 'brake_and'],
        ['on', 'crest', 'on_crest'],
        ['over', 'crest', 'over_crest'],
        ['crest', 'left', 'crest_left'],
        ['crest', 'right', 'crest_right'],
        ['until', 'finish', 'until_finish'],
        ['tightens', 'sumppu', 'tightens_sumppu'],
        ['big', 'sumppu', 'big_sumppu'],
        ['small', 'sumppu', 'small_sumppu'],
        ['onto', 'bridge', 'onto_bridge'],
        ['narrow', 'bridge', 'narrow_bridge'],
        ['onto', 'bridge', 'narrow', 'onto_bridge_narrow'],
    ]

    # obstacles
    obstacles = ['tree', 'rock', 'house', 'sign', 'post', 'junction', 'bridge', 'crest']
    for obstacle in obstacles:
        notes.append(['at', obstacle, 'at_' + obstacle])

    for dist in [20, 30, 40, 50]:
        notes.append(['brake', 'in', str(dist), 'brake_in_'+str(dist)])

    for c in ['small', 'long', '2', '3']:
        notes.append(['over', c, 'crest', 'over_'+c+'_crest'])

    descriptive = ['90_left', 'kleft', 'mediumleft', 'fastleft',
                   'easyleft', 'easyright', 'fastright', 'mediumright', 'kright',
                   '90_right', 'slowleft', 'slowright', 'flat_right', 'flat_left']

    for d in descriptive:
        notes.append([d, 'plus', d + '_plus'])

    # change to the directory
    os.chdir(args.dir)

    for note in notes:
        for i in range(1, 5):
            if i > 1:
                files = [ f+'_'+str(i)+'.ogg' for f in note]
            else:
                files = [ f+'.ogg' for f in note]
            if not all([os.path.exists(f) for f in files[:-1]]):
                logging.warning(f'Not all files exist: {files}')
                if i == 1:
                    logging.error('Exiting')
                    exit(1)
                continue
            command = ['sox'] + files
            logging.info(command)
            subprocess.run(command, check=True)

