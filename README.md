# Lyrics-in-Terminal
A script which displays lyrics of the current playing song in terminal.

>Currently, only supports Spotify & VLC media player music detection on GNU/Linux

- - - - 
#### Prerequisites
This script requires Python version 3.3 or newer and standard Python 3 packages.


### Installation
Clone the repository.
```sh
git clone https://github.com/Jugran/lyrics-in-terminal.git
```

### Usage
Make script executable and run
```sh
chmod +x lyrics.sh
./lyrics.sh
```
Default player is Spotify, if you want to show lyrics from VLC Media Player then pass vlc to ```lyrics.sh```.
```sh
./lyrics.sh vlc | less
```
For better experience, pipe the script's output to a terminal pager programs like ```less``` and ```more```.
```sh
./lyrics.sh | less
```
When piping to ```less```, use arrows or mouse wheel to scroll and ```q``` to exit.
If certain characters are missing or incorrect then pass -r (raw text mode) flag to less

```sh
./lyrics.sh | less -r 
```	

License
----
MIT
- - - -
