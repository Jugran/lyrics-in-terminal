from setuptools import setup, find_packages
from setuptools.command.install import install
import os

from lyrics import __version__, CONFIG_PATH

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PostInstallConfigUpdate(install):
    """Post-installation for config update"""

    def run(self):
        install.run(self)
        self.updateConfigFile()

    def updateConfigFile(self):
        if CONFIG_PATH.exists():
            from configparser import ConfigParser

            old_config = ConfigParser()
            old_config.read(CONFIG_PATH)

            new_config = ConfigParser()
            new_config.read('lyrics/lyrics.cfg')

            skip = True

            for section in old_config.sections():
                old_keys = {o for o in old_config[section]}
                new_keys = {n for n in new_config[section]}
                changes = new_keys ^ old_keys

                if len(changes) == 0:
                    continue
                else:
                    skip = False

                for option in new_keys:
                    fallback = new_config[section].get(option)
                    new_config[section][option] = old_config[section].get(option, fallback)

            if not skip:
                with open(CONFIG_PATH, 'w') as file:
                    new_config.write(file)


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
            'lyrics = lyrics.lyrics_in_terminal:main',
            'lyt = lyrics.lyrics_in_terminal:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        'dbus-python',
        'requests'
    ],
    extras_require={
        'mpd': ['python-mpd2'],
        'full': ['python-mpd2']
    },
    python_requires='>=3.7',
    cmdclass={
        'install': PostInstallConfigUpdate
    },
    include_package_data=True
)
