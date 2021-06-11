__module_name__ = "spotify"
__module_version__ = "1.0"
__module_description__ = "Plugin for Spotify integration by decrypt@freenode"

import hexchat
from threading import Timer
# import time
import subprocess
from pprint import pprint
# import sys
# import os
import shlex
import re

hexchat.prnt(f"Spotify for Hexchat (v{__module_version__})")

cmd_base      = 'dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2'
cmd_play      = f'{cmd_base} org.mpris.MediaPlayer2.Player.Play'
cmd_pause     = f'{cmd_base} org.mpris.MediaPlayer2.Player.Pause'
cmd_playpause = f'{cmd_base} org.mpris.MediaPlayer2.Player.PlayPause'
cmd_previous  = f'{cmd_base} org.mpris.MediaPlayer2.Player.Previous'
cmd_next      = f'{cmd_base} org.mpris.MediaPlayer2.Player.Next'
cmd_current   = f"{cmd_base} org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata'"

def get_current_track_and_name():
    metadata = subprocess.check_output(shlex.split(cmd_current), stderr=subprocess.STDOUT).decode()
    metadata = re.sub('\s+', ' ', metadata, flags=re.MULTILINE)
    track_id = re.search('string "mpris:trackid" variant string "(.+?)"', metadata).group(1)
    duration = int(re.search('string "mpris:length" variant uint64 (\d+)', metadata).group(1))
    url = re.search('string "xesam:url" variant string "(.+?)"', metadata).group(1)
    artist = re.search('string "xesam:artist" variant array \[ string "(.+?)"', metadata).group(1)
    title  = re.search('string "xesam:title" variant string "(.+?)..\)', metadata).group(1)
    name = artist + ' - ' + title
    minutes = int(duration / 60000000)
    seconds = int(60 * ((duration / 60000000) - minutes))
    formated = f'{minutes}:{seconds:02d}'
    return '%s (%s) URL: [ %s ]' % (name, formated, url)

def current_music():
    try:
        cmusic = get_current_track_and_name()
        hexchat.prnt(' ** SPOTIFY: %s' % cmusic)
    except Exception as inst:
        hexchat.prnt(' ** SPOTIFY not running')

def spotify(word, word_eol, userdata):
    subcommand = None
    if len(word) == 0:
        subcommand = cmd_current
    else:
        if len(word) == 2:
            switcher = {
                'current': cmd_current,
                'play': cmd_play,
                'pause': cmd_pause,
                'playpause': cmd_playpause,
                'prev': cmd_previous,
                'previous': cmd_previous,
                'next': cmd_next
            }
            subcommand = switcher.get(word[1], None)

    if subcommand is not None:
        if subcommand is cmd_current:
            try:
                cmusic = get_current_track_and_name()
                hexchat.command('me listening: %s' % cmusic)
            except Exception as inst:
                hexchat.prnt(' ** SPOTIFY not running')
        else:
            subprocess.check_output(shlex.split(subcommand))
            if subcommand is cmd_previous or subcommand is cmd_next:
                r = Timer(0.5, current_music, ())
                r.start()
    return hexchat.EAT_ALL


hexchat.hook_command('spotify', spotify)
