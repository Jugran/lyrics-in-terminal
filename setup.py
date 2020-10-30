from setuptools import setup, find_packages
from setuptools.command.install import install
import os

from lyrics import __version__
from config_update import updateChanges

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

class PostInstallConfigUpdate(install):
    """Post-installation for config update"""
    def run(self):
        install.run(self)
        updateChanges()

setup(
    name='lyrics-in-terminal',
    version=__version__,
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
    cmdclass={
        'install': PostInstallConfigUpdate
    },
    include_package_data=True
)
