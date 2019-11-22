#!/usr/bin/env python3

from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
import sys
import re


url = 'https://www.google.com/search?q='
header = {'User-Agent' : 'Mozilla/5.0'}

class_name = r'\w{5,7} \w{4,5} \w{5,7}'		# dependent on User-Agent and sometimes doesn't work

def get_html(url):

	req = Request(url, data=None, headers=header)
	req_url = urlopen(req)

	if req_url.code != 200:
		print('invalid request')
		exit(1)

	return req_url.read().decode('utf-8')


def format_lyrics(lyrics, width):
	lyrics_text = '\n'.join([line.center(width) for line in lyrics])
	# center lyrics vertically here

	return lyrics_text.replace('&amp;', '&')


def get_az_html(url):
	html = get_html(url.replace('lyrics', 'azlyrics'))

	regex = re.compile(r'(http[s]?://www.azlyrics.com/lyrics(?:.*?))&amp')
	az_url = regex.search(html)

	if az_url == None:
		print( 'No Lyrics Found!'.center(width))
		exit(0)
	else:

		header['User-Agent'] = 'Mozilla/5.0 Firefox/70.0'
		az_url = az_url.group(1)
		az_html = get_html(az_url)
		return az_html


def get_azlyrics(url, width):
	# print('azlyrics:')
	az_html = get_az_html(url)

	az_regex = re.compile(r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

	ly = az_regex.search(az_html)

	if ly == None:
		# Az lyrics not found
		return 'Azlyrics missing...'.center(width)

	ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()
	lyrics_text = format_lyrics(ly.split('\n'), width)

	return lyrics_text


def get_lyrics(url, width):

	html = get_html(url)
	html_regex = re.compile(r'<div class="{}">([^>]*?)</div>'.format(class_name), re.S)

	text_list = html_regex.findall(html)

	if len(text_list) < 2:
		# No google result found!
		lyrics_text = get_azlyrics(url, width)
	else:

		ly = []

		for l in text_list[1:]:
			# lyrics must be multiline, ignore the artist info below lyrics
			if l.count('\n') > 2:
				ly += l.split('\n')

		if len(ly) < 5:					# too short match for lyrics
			lyrics_text = get_azlyrics(url, width)
		else:
			# format lyrics
			lyrics_text = format_lyrics(ly, width)
			
	return lyrics_text


if __name__	== '__main__': 

	if len(sys.argv) > 1:

		track_name = '-'.join(sys.argv[1:-1])

		tr = sys.argv[1] + '-' + sys.argv[2]

		query = quote(tr + ' lyrics')

		width = int(sys.argv[-1])

	else:
		print('No Track info provided, Exiting...')
		exit

	print(track_name.center(width), (round(width * 0.8) * '-').center(width))

	lyrics = get_lyrics(url + query, width)

	print(lyrics)
