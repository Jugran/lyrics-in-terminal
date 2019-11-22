#!/bin/bash

ARTIST="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' | grep -A 3 artist | grep string | grep -v xesam | sed 's/^\s*//' | cut -d ' ' -f 2- | tr '(' ' ' | tr ')' ' ' | tr '"' ' ' )";

TITLE="$(dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' | grep -A 3 title | grep string | grep -v xesam | sed 's/^\s*//' | sed 's/^variant\s*//' | cut -d ' ' -f 2- | tr '"' ' ' )";

columns=$(tput cols)

(python3 lyrics.py "$ARTIST" "$TITLE" ${columns:-80})