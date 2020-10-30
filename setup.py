from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import re

from lyrics import __version__, CONFIG_PATH

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PostInstallConfigUpdate(install):
    """Post-installation for config update"""

    def run(self):
        install.run(self)
        self.updateChanges()

    def getContents(self, filename):
        with open(filename) as f:
            contents = f.read()
        return contents

    def getOptions(self, config):
        regex = r'(\w+)=.*'
        options = re.findall(regex, config)
        return set(options)

    def updateChanges(self):

        if CONFIG_PATH.exists():
            # check for changes
            old_config = self.getContents(CONFIG_PATH)
            new_config = self.getContents('lyrics/lyrics.cfg')
            new_options = self.getOptions(new_config) - self.getOptions(old_config)

            if len(new_options) == 0:
                return

            with open(CONFIG_PATH, 'a') as file:
                for option in new_options:
                    new_option = re.findall(fr'({option}=.*)', new_config)[0]
                    file.write(new_option + '\n')


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
