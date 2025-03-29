#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple
from urllib.parse import quote
from textwrap import wrap
from lyrics import CACHE_PATH

from subprocess import run
import os
import tempfile
import re
import requests


url = 'https://www.google.com/search?q='
HEADER = {
    'User-Agent': 'User-Agent: Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/0.8.12'
}

CLASS_NAME = r'\w{5,7} \w{4,5} \w{5,7}'  # dependent on User-Agent
EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file


def query(track_name):
    '''encodes search query
    '''
    track_name = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    return quote(track_name + ' lyrics')


def get_html(url, header=HEADER) -> str | Tuple[str, Exception]:
    ''' returns html text from given url
    '''
    try:
        resp = requests.get(url, headers=header)
        resp.raise_for_status()
    except Exception as e:
        # TODO: add error logging to file
        return 'Error:' + str(e), e

    return resp.text


def get_az_html(html: str) -> str | None:
    ''' finds azlyrics website link and
        returns html text from azlyrics

        if azlyrics link not found returns None
    '''
    regex = re.compile(r'(http[s]?://www.azlyrics.com/lyrics(?:.*?))&amp')
    az_url = regex.search(html)

    if az_url == None:
        return None

    header = {'User-Agent': 'Mozilla/5.0 Firefox/70.0'}
    az_url = az_url.group(1)
    az_html = get_html(az_url, header)

    if isinstance(az_html, tuple):
        return None
    return az_html


def get_genius_html(html: str) -> str | None:
    ''' finds genius website link and
        returns html text from genius

        if genius link not found returns None
    '''
    regex = re.compile(r'(http[s]?://genius.com/(?!albums)(?:.*?))&amp')
    gns_url = regex.search(html)

    if gns_url == None:
        return None

    gns_url = gns_url.group(1)
    gns_html = get_html(gns_url, header={})

    if isinstance(gns_html, tuple):
        return None
    return gns_html


def parse_genius(html: str | None) -> List[str] | None:
    ''' parses lyrics from genius html
        returns list if strings of lyrics or None if lyrics not found
    '''
    if html == None:
        return None

    gns_regex = re.compile(
        '<div data-lyrics-container="true" (?:.*?)(>.*?<)/div>', re.S)
    ly = gns_regex.findall(html)

    if ly == None:
        # Genius lyrics not found
        return None

    lyrics_lines = ''
    for ly_section in ly:
        ly_section = ly_section.replace('&#x27;', "'")
        line_regex = re.compile(r'>([^<]+?)<', re.S)
        lines = line_regex.findall(ly_section)
        lyrics_lines += "\n".join(lines)

    lyrics_lines = re.sub(r'\n{2,}', '\n', lyrics_lines)
    lyrics_lines = lyrics_lines.replace('\n[', '\n\n[').replace('&quot;', '"')

    lyrics_lines = lyrics_lines.split('\n')

    return lyrics_lines


def parse_azlyrics(html: str | None) -> List[str] | None:
    ''' parses lyrics from azlyrics html
        returns list if strings of lyrics

        if lyrics not found returns error string
    '''
    if html == None:
        return None

    az_regex = re.compile(
        r'Sorry about that. -->(.*)(?:<script>(.*))<!-- MxM banner -->', re.S)

    ly = az_regex.search(html)
    if ly == None:
        # Az lyrics not found
        return None

    # remove stray html tags
    ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()

    # replace html entities
    rep = {'&quot;': '\"', '&amp;': '&', '\r': ''}
    replace_patten = '|'.join(rep.keys())
    ly = re.sub(replace_patten, lambda match: rep[match.group(0)], ly)
    lyrics_lines = ly.split('\n')

    return lyrics_lines


def parse_google(html: str) -> List[str] | None:
    ''' parses google result html
        returns list of strings or None if no lyrics found
    '''
    html_regex = re.compile(
        r'<div class="{}">([^>]*?)</div>'.format(CLASS_NAME), re.S)

    text_list = html_regex.findall(html)

    if len(text_list) < 2:
        # No google result found!
        return None

    lyrics_lines = []
    for l in text_list[1:]:
        # lyrics must be multiline,
        # ignore the artist info below lyrics
        if l.count('\n') > 2:
            lyrics_lines += l.split('\n')
    if len(lyrics_lines) < 5:
        # too short match for lyrics
        return None

    return lyrics_lines


def get_filename(track_name):
    '''returns name of cache file name from track name with correct format
    '''
    # removing text in brackets [] ()
    filename = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    return os.path.join(CACHE_PATH, filename)


def get_lyrics(track_name: str, source: str = 'any', cache: bool = True) -> Tuple[List[str], str | None]:
    ''' returns tuple of list of strings with lines of lyrics and found source
        also reads/write to cache file | if cache=True

        track_name -> track name in format "artist - title"
        source -> source to fetch lyrics from ('google', 'azlyrics', 'genius', 'any')
        cache -> bool | whether to check lyrics from cache or not.
    '''
    filepath = get_filename(track_name)

    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    lyrics_lines = None
    # If cache enabled, then return cached lyrics
    if os.path.isfile(filepath) and cache:
        # cache lyrics exist
        with open(filepath) as file:
            lyrics_lines = file.read().splitlines()
        return lyrics_lines, 'cache'

    search_url = url + query(track_name)
    html = get_html(search_url)
    if isinstance(html, tuple):
        err = html[0]
        return [err], source

    found_source = None
    if source == 'google' or source == 'any':
        lyrics_lines = parse_google(html)
        found_source = 'google' if lyrics_lines is not None else None

    if source == 'azlyrics' or (source == 'any' and lyrics_lines is None):
        az_html = get_az_html(html)
        lyrics_lines = parse_azlyrics(az_html)
        found_source = 'azlyrics' if lyrics_lines is not None else None

    if source == 'genius' or (source == 'any' and lyrics_lines is None):
        gns_html = get_genius_html(html)
        lyrics_lines = parse_genius(gns_html)
        found_source = 'genius' if lyrics_lines is not None else None

    if lyrics_lines is None:
        return ['lyrics not found! :( for', source], source

    # TODO: replace all html entities with ASCII instead of just &amp;
    text = map(lambda x: x.replace('&amp;', '&') + '\n', lyrics_lines)

    with open(filepath, 'w') as file:
        file.writelines(text)

    return lyrics_lines, found_source or source


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
