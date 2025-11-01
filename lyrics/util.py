#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple
from urllib.parse import quote, unquote
from textwrap import wrap
from lyrics import CACHE_PATH

from subprocess import run
import os
import tempfile
import re
import requests
import random


URLS_CACHE = {
    "track": None,
    "urls": None
}


URLS = [
    {
        "name": "duckduckgo",
        "url": "https://duckduckgo.com/html/?q="
    },
    {
        "name": "frogfind",
        "url": "http://frogfind.com?q="
    }
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B435 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36 OPR/31.0.1889.174",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 7262.52.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.86 Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; en-gb; KFTT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.2; SM-T520 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.84 Safari/537.36",
    "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1"
]

EDITOR = os.environ.get('EDITOR', 'nano')
initial_text = b"Add lyrics here!"     # placeholder text for lyrics file


def query(track_name):
    '''encodes search query
    '''
    track_name = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    return quote(track_name + ' lyrics')


def get_html(url, header=None) -> str | Tuple[str, Exception]:
    ''' returns html text from given url
    '''
    try:
        if header is None:
            header = {'User-Agent': random.choice(USER_AGENTS)}
            # header = {}
        resp = requests.get(url, headers=header)
        resp.raise_for_status()
    except Exception as e:
        # TODO: add error logging to file
        return 'Error:' + str(e), e

    return resp.text


def get_az_html(links: List[str]) -> str | None:
    ''' finds azlyrics website link and
        returns html text from azlyrics

        if azlyrics link not found returns None
    '''
    az_url = next((l for l in links if 'azlyrics.com' in l), None)

    if az_url == None:
        return None

    header = {'User-Agent': 'Mozilla/5.0 Firefox/70.0'}
    az_html = get_html(az_url, header)

    if isinstance(az_html, tuple):
        return None
    return az_html


def get_genius_html(links: List[str]) -> str | None:
    ''' finds genius website link and
        returns html text from genius

        if genius link not found returns None
    '''
    gns_url = next((l for l in links if 'genius.com' in l), None)

    if gns_url == None:
        return None

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
        '<div data-lyrics-container="true" (?:.*?)(>.*?)<div class="LyricsFooter', re.S)
    ly = gns_regex.findall(html)

    if ly == None:
        # Genius lyrics not found
        return None

    lyrics_lines = ''
    line_regex = re.compile(r'>([^<]+?)<', re.S)
    for ly_section in ly:
        ly_section = ly_section.replace('&#x27;', "'")
        lines = line_regex.findall(ly_section)
        for line in lines:
            # skip contributor info and meta
            if lyrics_lines == '' and line[0] != '[':
                continue
            lyrics_lines += line + '\n'

    lyrics_lines = re.sub(r'\n{2,}', '\n', lyrics_lines)
    lyrics_lines = lyrics_lines.replace('\n[', '\n\n[').replace('&quot;', '"')

    lyrics_lines = lyrics_lines.split('\n')

    lyrics_lines = [line.strip() for line in lyrics_lines if line.strip() != '']

    return lyrics_lines if len(lyrics_lines) > 0 else None


def parse_azlyrics(html: str | None) -> List[str] | None:
    ''' parses lyrics from azlyrics html
        returns list if strings of lyrics

        if lyrics not found returns error string
    '''
    if html == None:
        return None

    az_regex = re.compile(
        r'Sorry about that. -->(.*)(?:<script>(.*?))?<!-- MxM banner -->', re.S)

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


def get_urls(engine, html):
    ''' parses url redirect links from html
        returns list of strings with parsed links
    '''

    links = None

    if engine == 'frogfind':
        url_regex = re.compile(r'href="?(?:.*?)a=(.*?)[\\\']')
        links = url_regex.findall(html)
    elif engine == 'duckduckgo':
        ddg_regex = re.compile(r'//duckduckgo\.com/l/\?uddg=(.*?)[;\"]')
        links = ddg_regex.findall(html)

        # check for non ddg redirect links
        if links is None or len(links) == 0:
            url_regex = re.compile(r'href="(?!\/\/)(.*?)[;\"]')
            links = url_regex.findall(html)

    if links is None or len(links) == 0:
        return []
    parsed = []
    for link in links:
        parsed_link = unquote(link).replace("&amp", "")
        parsed.append(parsed_link)
    return parsed


def get_filename(track_name):
    '''returns name of cache file name from track name with correct format
    '''
    # removing text in brackets [] ()
    filename = re.sub(r'(\[.*\].*)|(\(.*\).*)', '', track_name).strip()
    filename = re.sub(r'\s|\/|\\|\.', '', filename)
    return os.path.join(CACHE_PATH, filename)


def fetch_urls(track_name: str) -> List[str]:
    ''' fetches urls for given track name from search
        returns list of strings with parsed links
    '''
    if URLS_CACHE["track"] == track_name and URLS_CACHE["urls"] is not None:
        return URLS_CACHE["urls"]

    q = query(track_name)
    result_urls = []
    for url in URLS:
        search_url = url["url"] + q
        html = get_html(search_url)
        if isinstance(html, tuple):
            err = html[0]
            continue
        result_urls = get_urls(url["name"], html)
        if len(result_urls) < 10:
            # try next search engine, results too less
            continue
        URLS_CACHE["track"] = track_name
        URLS_CACHE["urls"] = result_urls
        break

    return result_urls


def get_lyrics(track_name: str, source: str = 'any', cache: bool = True) -> Tuple[List[str], str | None]:
    ''' returns tuple of list of strings with lines of lyrics and found source
        also reads/write to cache file | if cache=True

        track_name -> track name in format "artist - title"
        source -> source to fetch lyrics from ('azlyrics', 'genius', 'any')
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

    #  check cached urls for track

    urls = fetch_urls(track_name)

    found_source = None
    if source == 'azlyrics' or (source == 'any' and lyrics_lines is None):
        az_html = get_az_html(urls)
        lyrics_lines = parse_azlyrics(az_html)
        found_source = 'azlyrics' if lyrics_lines is not None else None

    if source == 'genius' or (source == 'any' and lyrics_lines is None):
        gns_html = get_genius_html(urls)
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
