# Lyrics-in-Terminal


>Currently, only supports Spotify & VLC media player music detection on GNU/Linux

- - - - 
## Installation
##### From PyPi
```sh
pip install lyrics-in-terminal
```

## Usage
```sh
lyrics
```
Default player is Spotify, if you want to show lyrics from VLC Media Player then pass vlc as an argument
```sh
lyrics vlc
```

### Keybindings

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
| Quit Program        | <kbd>q</kbd>  |

- Update Lyrics: Deletes local cached lyrics and fetches lyrics from the internet. 

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

