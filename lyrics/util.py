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
from pathlib import Path
import sys


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
    lyrics_lines = lyrics_lines.replace('\n[', '\n\n[')

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
        r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

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


def get_lyrics(track_name: str, source: str = 'any', cache: bool = True) -> Tuple[List[str], List[float] | None, str | None]:
    ''' returns tuple of list of strings with lines of lyrics, timestamps and found source
        also reads/write to cache file | if cache=True

        track_name -> track name in format "artist - title"
        source -> source to fetch lyrics from ('google', 'azlyrics', 'genius', 'any')
        cache -> bool | whether to check lyrics from cache or not.
        
        Returns:
            Tuple of (lyrics_list, timestamps_list, source)
            timestamps_list will be None for non-LRC sources
    '''
   
    # Clean up track name for searching
    search_name = track_name.strip(' -')
    
    # First check for .lrc file
    lrc_path = get_filename(track_name, lrc=True)
    
    if os.path.isfile(lrc_path):
        with open(lrc_path, 'r', encoding='utf-8') as file:
            lrc_lines = file.read().splitlines()
            
            # Parse LRC lines with timestamps
            timed_lyrics = []
            for line in lrc_lines:
                results = parse_lrc_line(line)
                timed_lyrics.extend(results)  # Add all timestamp-lyric pairs
            
            if timed_lyrics:
                # Sort by timestamp and remove duplicates
                timed_lyrics.sort(key=lambda x: x[0])
                
                # Keep track of unique lyrics while preserving order
                seen_lyrics = {}  # text -> timestamp
                lyrics_list = []
                timestamps_list = []
                
                for timestamp, text in timed_lyrics:
                    if text not in seen_lyrics:
                        seen_lyrics[text] = timestamp
                        lyrics_list.append(text)
                        timestamps_list.append(timestamp)
                
                return (lyrics_list, timestamps_list, 'lrc')
    
    # Check regular lyrics cache
    filepath = get_filename(track_name)

    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    lyrics_lines = None
    # If cache enabled, then return cached lyrics
    if os.path.isfile(filepath) and cache:
        # cache lyrics exist
        with open(filepath) as file:
            lyrics_lines = file.read().splitlines()
        return (lyrics_lines, None, 'cache')

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
