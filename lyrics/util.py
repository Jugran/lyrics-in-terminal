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
HEADER = {
    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch'
}

CLASS_NAME = r'\w{5,7} \w{4,5} \w{5,7}'  # dependent on User-Agent
EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file


def query(track_name):
    '''encodes search query
    '''
    track_name = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    return quote(track_name + ' lyrics')


def get_html(url, header=HEADER):
    ''' returns html text from given url
    '''
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
    ''' finds azlyrics website link and
        returns html text from azlyrics

        if azlyrics link not found returns error string
    '''
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
    ''' fetches lyrics from azlyrics
        returns list if strings of lyrics

        if lyrics not found returns error string
    '''
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
    ''' fetches sources from google, then azlyrics 
        checks if lyrics are valid 

        returns list of strings 

        if lyrics not found in both google & azlyrics
        returns string of error from get_azlyrics()
    '''
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
    '''returns name of cache file name from track name with correct format
    '''
    # removing text in brackets [] ()
    filename = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    return os.path.join(CACHE_PATH, filename)


def get_lyrics(track_name, source, cache=True):
    ''' returns list of strings with lines of lyrics
        also reads/write to cache file | if cache=True

        track_name -> track name in format "artist - title"
        source -> source to fetch lyrics from ('google' or 'azlyrics')
        cache -> bool | whether to check lyrics from cache or not.
    '''
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
