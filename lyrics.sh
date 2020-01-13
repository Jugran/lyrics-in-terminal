#!/bin/bash

PLAYER="$1"
PLAYER="spotify"

ARTIST="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.$PLAYER /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' | grep -A 3 'string "xesam:artist"' | grep -A 1 variant | grep -oP '"\K[^"]+' | tr -d '\n' )";

TITLE="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.$PLAYER /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' | grep -A 3 'string "xesam:title"' | grep variant | grep -oP '"\K[^"]+' | tr -d '\n' )";

columns=$(tput cols)
rows=$(tput lines)
(python3 lyrics.py "$ARTIST " " $TITLE" ${columns:-80} $rows)


#TODO: priority order check for different players for lyrics
