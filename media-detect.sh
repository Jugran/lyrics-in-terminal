#!/bin/sh

for m in `qdbus | egrep -i 'org.mpris.MediaPlayer2|plasma-browser-integration'` ; do
    if [[ `qdbus $m /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlaybackStatus` == 'Playing' ]]; then
        echo $m 
        qdbus $m /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Metadata
    fi
done



## pulsectl for python
# https://github.com/mk-fg/python-pulse-control
