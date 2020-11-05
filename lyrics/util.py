#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import quote
from textwrap import wrap
from lyrics import CACHE_PATH

from subprocess import run
import os
import tempfile
import re


url = 'https://www.google.com/search?q='
HEADER = {'User-Agent': 'Mozilla/5.0'}

CLASS_NAME = r'\w{5,7} \w{4,5} \w{5,7}'  # dependent on User-Agent
EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file


def query(track_name):
    """
    Query the track_name.

    Args:
        track_name: (str): write your description
    """
    return quote(track_name + ' lyrics')


def get_html(url, header=HEADER):
    """
    Download html from url.

    Args:
        url: (str): write your description
        header: (str): write your description
        HEADER: (str): write your description
    """
    try:
        req = Request(url, data=None, headers=header)
        req_url = urlopen(req)
    except Exception as e:
        return 'Cannot connect to internet!', e

    if req_url.code != 200:
        print('invalid request')
        exit(1)

    return req_url.read().decode('utf-8')


def get_az_html(url):
    """
    Get azure azure url.

    Args:
        url: (str): write your description
    """
    html = get_html(url.replace('lyrics', 'azlyrics'))
    if isinstance(html, tuple):
        return html

    regex = re.compile(r'(http[s]?://www.azlyrics.com/lyrics(?:.*?))&amp')
    az_url = regex.search(html)

    if az_url == None:
        return 'No Lyrics Found!'
    else:
        header = {'User-Agent': 'Mozilla/5.0 Firefox/70.0'}
        az_url = az_url.group(1)
        az_html = get_html(az_url, header)
        return az_html


def get_azlyrics(url):
    """
    Get azure url.

    Args:
        url: (str): write your description
    """
    az_html = get_az_html(url)
    if isinstance(az_html, tuple):
        return az_html[0]

    az_regex = re.compile(
        r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

    ly = az_regex.search(az_html)
    if ly == None:
        # Az lyrics not found
        return 'Azlyrics missing...'

    rep = {'&quot;': '\"', '&amp;': '&', '\r': ''}

    ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()
    # ly = ly.replace('&quot;', '\"').replace('&amp;', '&')
    # regex = re.compile('|'.join(substrings))
    ly = re.sub('|'.join(rep.keys()), lambda match: rep[match.group(0)], ly)
    lyrics_lines = ly.split('\n')

    return lyrics_lines


def fetch_lyrics(url):
    """
    Fetch the given url.

    Args:
        url: (str): write your description
    """
    html = get_html(url)
    if isinstance(html, tuple):
        return html[0]

    html_regex = re.compile(
        r'<div class="{}">([^>]*?)</div>'.format(CLASS_NAME), re.S)

    text_list = html_regex.findall(html)

    if len(text_list) < 2:
        # No google result found!
        lyrics_lines = get_azlyrics(url)
    else:
        ly = []
        for l in text_list[1:]:
            # lyrics must be multiline,
            # ignore the artist info below lyrics
            if l.count('\n') > 2:
                ly += l.split('\n')
        if len(ly) < 5:
            # too short match for lyrics
            lyrics_lines = get_azlyrics(url)
        else:
            # format lyrics
            lyrics_lines = ly

    return lyrics_lines


def get_filename(track_name):
    """
    Get the filename of a track.

    Args:
        track_name: (str): write your description
    """
    filename = track_name.strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    return os.path.join(CACHE_PATH, filename)


def get_lyrics(track_name, source, cache=True):
    """
    Retrieves the track_name for a track.

    Args:
        track_name: (str): write your description
        source: (str): write your description
        cache: (todo): write your description
    """
    filepath = get_filename(track_name)

    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    if os.path.isfile(filepath) and cache:
        # lyrics exist
        with open(filepath) as file:
            lyrics_lines = file.read().splitlines()
    else:
        if source == 'google':
            lyrics_lines = fetch_lyrics(url + query(track_name))
        else:
            lyrics_lines = get_azlyrics(url + query(track_name))

        if isinstance(lyrics_lines, str):
            return ['lyrics not found! :(', 'Issue is:', lyrics_lines]

        text = map(lambda x: x.replace('&amp;', '&') + '\n', lyrics_lines)

        with open(filepath, 'w') as file:
            file.writelines(text)

    return lyrics_lines


def edit_lyrics(track_name):
    """
    Edit track_name.

    Args:
        track_name: (str): write your description
    """
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
        
        with open(filepath, 'w') as file:
            file.writelines(edited_lyrics)



def delete_lyrics(track_name):
    """
    Delete a track_name from the track

    Args:
        track_name: (str): write your description
    """
    filepath = get_filename(track_name)

    if os.path.isfile(filepath):
        # lyrics exist
        os.remove(filepath)
        return True

    return False


def align(lines, width, alignment=1):
    """
    Aligns all lines in lines.

    Args:
        lines: (list): write your description
        width: (int): write your description
        alignment: (str): write your description
    """
    if alignment == 1:
        return lines
    elif alignment == 0:
        return [line.center(width) for line in lines]
    else:
        return [line.rjust(width - 1) for line in lines]


def wrap_text(text, width):
    """
    Wrap text in a list of lines.

    Args:
        text: (str): write your description
        width: (int): write your description
    """
    lines = []
    for line in text:
        if len(line) > width:
            line = wrap(line, width=width)
        if isinstance(line, list):
            lines += line
        else:
            lines.append(line)

    return lines
