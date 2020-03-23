#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import quote
from textwrap import wrap
import os
import re


url = 'https://www.google.com/search?q='
HEADER = {'User-Agent': 'Mozilla/5.0'}

CLASS_NAME = r'\w{5,7} \w{4,5} \w{5,7}'  # dependent on User-Agent 

# location for cache
CACHE_PATH = os.path.join(os.environ['HOME'], '.cache', 'lyrics')


def query(track_name):
    return quote(track_name + ' lyrics')


def get_html(url, header=HEADER):
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
    az_html = get_az_html(url)
    if isinstance(az_html, tuple):
        return az_html[0]

    az_regex = re.compile(r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

    ly = az_regex.search(az_html)
    if ly == None:
        # Az lyrics not found
        return 'Azlyrics missing...'

    rep = {'&quot;': '\"', '&amp;': '&', '\r' : ''}

    ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()  
    # ly = ly.replace('&quot;', '\"').replace('&amp;', '&')
    # regex = re.compile('|'.join(substrings))
    ly = re.sub('|'.join(rep.keys()), lambda match: rep[match.group(0)], ly)
    lyrics_lines = ly.split('\n')

    return lyrics_lines


def fetch_lyrics(url):
    html = get_html(url)
    if isinstance(html, tuple):
        return html[0]

    html_regex = re.compile(r'<div class="{}">([^>]*?)</div>'.format(CLASS_NAME), re.S)

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


def get_lyrics(track_name, source, cache=True):
    filename = track_name.strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    filepath = os.path.join(CACHE_PATH, filename)

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

        text = map(lambda x : x.replace('&amp;', '&') + '\n', lyrics_lines)
        
        with open(filepath, 'w') as file:
            file.writelines(text)

    return lyrics_lines


def delete_lyrics(track_name):
    filename = track_name.strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    filepath = os.path.join(CACHE_PATH, filename)

    if os.path.isfile(filepath):                
        # lyrics exist
        os.remove(filepath)
        return True
    
    return False


def align(lines, width, alignment=1):
    if alignment == 1:
        return lines
    elif alignment == 0:
        return [line.center(width) for line in lines]
    else:
        return [line.rjust(width - 1) for line in lines]


def wrap_text(text, width):
    lines = []
    for line in text:
        if len(line) > width:
            line = wrap(line, width=width)
        if isinstance(line, list):
            lines += line
        else:
            lines.append(line)

    return lines
