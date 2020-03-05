from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='lyrics-in-terminal',
	version='1.0.1',
	description='Command Line Lyrics fetcher from mpris media player like Spotify, VLC, Audacious',
	author='Samarth Jugran',
	author_email='jugransamarth@gmail.com',
	license='MIT',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Jugran/lyrics-in-terminal',
	packages=find_packages(),
	entry_points={
		'console_scripts': [
			'lyrics = lyrics.lyrics_in_terminal:start'
		]
	},
	classifiers=[ 
		"Programming Language :: Python :: 3",
	    "License :: OSI Approved :: MIT License",
	    "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
    	'dbus-python'
    ],
    python_requires='>=3.6',
    include_package_data=True
)