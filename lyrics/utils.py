#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from textwrap import wrap
from typing import List, Tuple
from lyrics import CACHE_PATH

from subprocess import run
import os
import tempfile
import re

EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file



def get_filename(track_name, lrc=False):
    '''returns name of cache file name from track name with correct format

    Args:
        track_name: track name in format "artist - title"
        lrc: if True, look for .lrc file instead of plain lyrics
    '''
    # Clean up leading/trailing spaces and hyphens
    filename = track_name.strip(' -')

    # removing text in brackets [] ()
    filename = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', filename).strip()

    # Remove spaces and special characters
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    # Add .lrc extension if needed
    if lrc:
        filename = filename + '.lrc'

    # Build full path
    full_path = os.path.join(CACHE_PATH, filename)
    return full_path


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




def parse_lrc_line(line: str) -> List[Tuple[float, str]]:
    """Parse a single LRC line and return list of (timestamp, lyrics) pairs.

    Args:
        line: A line from LRC file, possibly with multiple timestamps
              e.g. "[00:12.34][00:15.67]Lyrics text"

    Returns:
        List of tuples (timestamp in seconds, lyrics text)
    """
    if not line or not line.startswith('['):
        return []

    try:
        # Find all timestamps in the line
        timestamps = []
        lyrics_text = line

        while lyrics_text.startswith('['):
            bracket_end = lyrics_text.find(']')
            if bracket_end == -1:
                break

            timestamp_str = lyrics_text[1:bracket_end]  # "00:12.34"

            try:
                if ':' in timestamp_str:
                    minutes, seconds = timestamp_str.split(':')
                    total_seconds = float(minutes) * 60 + float(seconds)
                    timestamps.append(total_seconds)
            except ValueError:
                pass  # Skip invalid timestamps

            lyrics_text = lyrics_text[bracket_end + 1:]

        lyrics_text = lyrics_text.strip()
        if not lyrics_text or not timestamps:
            return []

        # Return a pair for each timestamp with the same lyrics
        return [(ts, lyrics_text) for ts in timestamps]

    except Exception as e:
        return []


def format_synced_lyrics(lyrics_lines: List[str]) -> Tuple[List[str], List[float]]:
    '''Returns a tuple of (lyrics_list, timestamps_list).

    Args:
        lyrics_lines: List of strings, each string is a line from a LRC file.

    Returns:
        A tuple of:
            - lyrics_list: List of strings, each string is a line of lyrics.
            - timestamps_list: List of floats, each float is a timestamp in seconds.
            - 'lrc': A string indicating the source of the lyrics.
    '''
    lyrics = []
    for line in lyrics_lines:
        results = parse_lrc_line(line)
        lyrics.extend(results)  # Add all timestamp-lyric pairs

    # Sort by timestamp and remove duplicates
    lyrics.sort(key=lambda x: x[0])

    lyrics_list = []
    timestamps_list = []

    for timestamp, text in lyrics:
        lyrics_list.append(text)
        timestamps_list.append(timestamp)

    return (lyrics_list, timestamps_list)