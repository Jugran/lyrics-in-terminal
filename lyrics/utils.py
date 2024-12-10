#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from textwrap import wrap
from lyrics import CACHE_PATH

from subprocess import run
import os
import tempfile
import re

EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file


def get_filename(track_name):
    '''returns name of cache file name from track name with correct format
    '''
    # removing text in brackets [] ()
    filename = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    return os.path.join(CACHE_PATH, filename)


def edit_lyrics(track_name):
    ''' opens local lyrics file in $EDITOR to edit
        if $EDITOR is not set, defaults to nano

        if local lyrics file does not exists, 
        then opens temp file
    '''
    filepath = get_filename(track_name)

    if os.path.isfile(filepath):
        # lyrics exist
        # open text file
        run([EDITOR, filepath], check=True)
    else:
        # open temp file
        with tempfile.NamedTemporaryFile(prefix=track_name, suffix=".tmp") as tf:
            tf.write(initial_text)
            tf.flush()
            run([EDITOR, tf.name])
            tf.seek(0)
            edited_lyrics = tf.read().decode('utf-8')
        # save temp file as lyrics cache
        with open(filepath, 'w') as file:
            file.writelines(edited_lyrics)


def delete_lyrics(track_name):
    ''' deletes local lyrics cache file
        returns -> bool | whether the delete operation occured or not
    '''
    filepath = get_filename(track_name)

    if os.path.isfile(filepath):
        # lyrics exist
        os.remove(filepath)
        return True

    return False


def align(lines, width, alignment=1):
    ''' returns list of strings with text alignment

        lines -> list of strings to align
        width -> width of viewport
        alignment -> integer [1 ,0 , n]

        0 = center alignment
        1 = left alignment (default)
        n = right alignment
    '''
    if alignment == 1:
        return lines
    elif alignment == 0:
        return [line.center(width) for line in lines]
    else:
        return [line.rjust(width - 1) for line in lines]


def wrap_text(text, width):
    ''' returns list of strings wrapped accross viewport

        text -> list of strings to wrap
        width -> width of viewport to fit text in
    '''
    lines = []
    for line in text:
        if len(line) > width:
            line = wrap(line, width=width)
        if isinstance(line, list):
            lines += line
        else:
            lines.append(line)

    return lines
