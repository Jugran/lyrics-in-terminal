# Lyrics-In-Terminal
[![GitHub release](https://img.shields.io/github/release/Jugran/lyrics-in-terminal/all.svg)](https://github.com/Jugran/lyrics-in-terminal/releases)
[![GitHub license](https://img.shields.io/github/license/Jugran/lyrics-in-terminal.svg)](https://github.com/Jugran/lyrics-in-terminal/blob/master/LICENSE)
[![PyPI version shields.io](https://img.shields.io/pypi/v/lyrics-in-terminal.svg)](https://pypi.python.org/pypi/lyrics-in-terminal/)

Shows lyrics of songs from your favourite music player in terminal.

![lyrics](https://raw.githubusercontent.com/Jugran/lyrics-in-terminal/master/images/001.png)
![lyrics](https://raw.githubusercontent.com/Jugran/lyrics-in-terminal/master/images/003.png)

## Supported Players
Almost all of the mpris specification compliant media players are supported, including -
* Spotify
* VLC Media player
* Rhythmbox
* Audacious


## Requirements
* Python >= 3.6
* dbus-python
* curses


## Installation

### From PyPi
```sh
pip install lyrics-in-terminal
```
> If pip install fails, then try installing python-dbus package from your distribution's repository first.

### From Source
First install dbus-python from your distribution's repository.

##### Debian and Ubuntu
```sh
sudo apt install python-dbus
```
##### Arch Linux
```sh
sudo pacman -S python-dbus
```
Install from source
```sh
git clone https://github.com/Jugran/lyrics-in-terminal.git
cd lyrics-in-terminal
pip install . --user
```

## Usage
```sh
$ lyrics
```
Default player is Spotify, if you want to show lyrics from some other then pass player name as an argument
```sh
$ lyrics {playername}

$ lyrics vlc
$ lyrics audacious
$ lyrics rhythmbox
```

### Default Keybindings

| Action              | Keybinding    											|
|:-------------------:|:-------------------------------------------------------:|
| Scroll Up           | <kbd>Up Arrow \| ↑</kbd> / <kbd>Mouse wheel Up</kbd> 	|
| Scroll Down         | <kbd>Down Arrow \| ↓</kbd>/ <kbd> Mouse wheel Down</kbd>|
| Scroll Up (5 steps) | <kbd>Left Arrow \| ← </kbd> 							|
| Scroll Down (5 steps)| <kbd>Right Arrow \| →</kbd>  							|
| Align Text Right         | <kbd>l</kbd>  |
| Align Text Center        | <kbd>k</kbd>  |
| Align Text Left          | <kbd>j</kbd>  |
| Update Lyrics<br>(from Azlyrics)    | <kbd>r</kbd>  |
| Update Lyrics<br>(from Google)    | <kbd>R</kbd>  |
| Delete lyrics file 		| <kbd>d</kbd> |
| Quit Program        | <kbd>q</kbd>  |

- Update Lyrics: Deletes local cached lyrics and fetches lyrics from the internet.
- Delete Lyrics: Deletes local lyrics text file from ```~/.cache/lyrics/{trackname}```

### Configuration

Config file is located in ```~/.local/lib/python3.x/site-packages/lyrics/lyrics.cfg```

<b>File Format</b>

```
# config structure
[SECTION]
option=value

---------------------------------------------------------------

#DEFAULT OPTIONS
[OPTIONS]
alignment=left
source=google
interval=1500
player=spotify

[BINDINGS]

#scroll
up=arrow_up
down=arrow_down
step-up=arrow_left
step-down=arrow_right
step-size=5

#source switch key
google=R
azLyrics=r

#text alignment
left=j
center=k
right=l

delete=d
quit=q
```


License
----
MIT
- - - -
<!-- 
##### Using different pager
If you dont want to install extra ```python-dbus``` package and want to use external pager program like ```less``` and ```more```, then execute ```lyrics.sh``` script instead.

First install from source
```sh
git clone https://github.com/Jugran/lyrics-in-terminal.git
cd lyrics-in-terminal
chmod +x install.sh
./install.sh
```
Then you can pipe the output of the script.
```sh
lyrics | less
lyrics vlc | less
```
>Note: The bash script does not have auto track change detection capability.

If certain characters are missing or incorrect then pass -r (raw text mode) flag to less.

```sh
lyrics | less -r 
```	 -->

