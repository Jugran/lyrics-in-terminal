#!/usr/bin/env python3

from urllib.request import urlopen, Request
from urllib.parse import quote
import sys
import re


url = 'https://www.google.com/search?q='
header = {'User-Agent' : 'Mozilla/5.0 Firefox'}

class_name = 'BNeawe tAd8D AP7Wnd'		# dependent on User-Agent and sometimes doesn't work
										# artist/ablum info <div class='BNeawe uEec3 AP7Wnd' >

def get_html(url):

	req = Request(url, data=None, headers=header)
	req_url = urlopen(req)

	if req_url.code != 200:
		print('invalid request')
		exit

	return req_url.read().decode('utf-8')


def get_azlyrics(html, width):
	regex = re.compile(r'(http[s]?://www.azlyrics.com/lyrics(?:.*?))&amp')
	url_list = regex.findall(html)

	if len(url_list) == 0:
			html = get_html(url + query.replace('lyrics', 'azlyrics'))
			return get_azlyrics(html, width)

	az_html = get_html(url_list[0])

	az_regex = re.compile(r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

	ly = az_regex.search(az_html)

	if ly == None:
		# Az lyrics not found
		return 'Azlyric missing...'.center(width)

	ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()

	lyrics_text = '\n'.join([l.center(width) for l in ly.split('\n')])

	return lyrics_text


def get_lyrics(query, width):

	html = get_html(url + query)
	html_regex = re.compile(r'<div class="{}">(.*?)</div>'.format(class_name), re.S)

	ly = '\n'.join(html_regex.findall(html)).split('\n')

	lyrics_text = '\n'.join([ l.center(width) for l in ly ])

	if len(ly) <= 1:
		# No google result found!
		# try azlyrics
		lyrics_text = get_azlyrics(html, width)

	if len(lyrics_text) <= 2 * width:
		if lyrics_text.replace('\n', ' ').strip() == '':
			lyrics_text = 'No Lyrics Found!'.center(width)

	return lyrics_text


if len(sys.argv) > 1:

	track_name = '-'.join(sys.argv[1:-1])

	query = quote(track_name + ' lyrics')

	width = int(sys.argv[-1])

else:
	print('No Track info provided, Exiting...')
	exit

print(track_name.center(width), (round(width*0.8) * '-').center(width))

lyrics = get_lyrics(url + query, width)

print(lyrics)
