#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import quote
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

    req = Request(url, data=None, headers=header)
    req_url = urlopen(req)

    if req_url.code != 200:
        print('invalid request')
        exit(1)

    return req_url.read().decode('utf-8')


def get_az_html(url):

    html = get_html(url.replace('lyrics', 'azlyrics'))
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
    az_regex = re.compile(r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

    ly = az_regex.search(az_html)
    if ly == None:
        # Az lyrics not found
        return 'Azlyrics missing...'

    ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()
    lyrics_lines = ly.split('\n')

    return lyrics_lines


def fetch_lyrics(url):

    html = get_html(url)
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


def get_lyrics(track_name):
        # check save cache for lyrics

    filename = track_name.strip().replace(' ', '')
    filepath = os.path.join(CACHE_PATH, filename)

    if  not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    if os.path.isfile(filepath):                
        # lyrics exist
        with open(filepath) as file:
            lyrics_lines = file.read().splitlines()
    else:
        lyrics_lines = fetch_lyrics(url + query(track_name))
        
        if isinstance(lyrics_lines, str):
            return ['lyrics not found! :(', 'Issue is:', lyrics_lines]

        text = map(lambda x : x.replace('&amp;', '&') + '\n', lyrics_lines)
        
        with open(filepath, 'w') as file:
            file.writelines(text)

    return lyrics_lines
