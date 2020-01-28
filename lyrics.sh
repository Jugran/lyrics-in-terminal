#!/bin/bash

PLAYER=${1:-"spotify"}

ARTIST="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.$PLAYER /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' 2>/dev/null | grep -A 3 'string "xesam:artist"' | grep -A 1 variant | grep -oP '"\K[^"]+')";

TITLE="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.$PLAYER /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' 2>/dev/null | grep -A 3 'string "xesam:title"' | grep variant | grep -oP '"\K[^"]+')";


if [ $? -ne 0 ]; then
	echo "$PLAYER not running! ..."
	exit 0
else
	ARTIST=$(echo $ARTIST | tr -d '\n')
	TITLE=$(echo $TITLE | tr -d '\n')
fi

columns=$(tput cols)
rows=$(tput lines)
(python3 track.py "$ARTIST " " $TITLE" ${columns:-80} $rows)


#TODO: priority order check for different players for lyrics
