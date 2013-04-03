# -*- coding: utf-8 -*-

'''
@author: plule

Copyright (C) 2013 plule

This file is part of XBMC Bandcamp Plugin.
'''



import sys,time,datetime,os
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
import urllib,urllib2,urlparse
import re
import sys

__addon__ =xbmcaddon.Addon('plugin.audio.bandcamp')
debugenabled=(__addon__.getSetting('debug')=='true')
baseDir = __addon__.getAddonInfo('path')

resDir = xbmc.translatePath(os.path.join(baseDir, 'resources'))
libDir = xbmc.translatePath(os.path.join(resDir,  'lib'))
datDir=  xbmc.translatePath(os.path.join(resDir,  'data'))
keyFile = xbmc.translatePath(os.path.join(datDir, 'key.txt'))

sys.path.append(libDir)
import bandcamp as bc
print sys.argv
plugin_url=str(sys.argv[0])
plugin_handle=int(sys.argv[1])
plugin_arguments=str(sys.argv[2])[1:]


MODE_HOME = 'home'
MODE_BAND = 'band'
MODE_ALBUM = 'album'
MODE_PLAY = 'play'
MODE_SEARCH = 'search'

def dbg(text):
    print('BANDCAMP =='+text)

def call_plugin_url(mode, args):
    return plugin_url+'?'+urllib.urlencode(dict({'mode':mode}.items() + args.items()))

def band_list(bands):
    xbmcplugin.setContent(plugin_handle, 'artists')
    for band in bands:
        listitem=xbmcgui.ListItem(band['name'] + ' (' + band['subdomain'] + ')')
        url=call_plugin_url(MODE_BAND, {'band_id':band['band_id']})
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=listitem, isFolder=True)
    xbmcplugin.endOfDirectory(handle=plugin_handle, succeeded=True)

def album_list(albums):
    xbmcplugin.setContent(plugin_handle, 'albums')
    sorted_albums = sorted(albums, key=lambda album: album['release_date'])
    for album in sorted_albums:
        year = datetime.datetime.fromtimestamp(int(album['release_date'])).year
        listitem=xbmcgui.ListItem(str(year) + ' - ' + album['title'], iconImage=album['large_art_url'])
        band = bc.band_info(album['band_id'])
        infos= {
            'year':year,
            'album':album['title'],
            'artist':band['name']
            }
        listitem.setInfo('Music', infos)
        listitem.setLabel2('atariesatinerastuenarusteanurs')

        play_album_url = 'XBMC.runPlugin('+call_plugin_url(MODE_PLAY, {'album_id':album['album_id']})+')'
        listitem.addContextMenuItems([('Play Album', play_album_url,)])
        
        url=call_plugin_url(MODE_ALBUM, {'album_id':album['album_id']})
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=listitem, isFolder=True)
    xbmcplugin.endOfDirectory(handle=plugin_handle, succeeded=True)

def track_list(tracks):
    xbmcplugin.setContent(plugin_handle, 'songs')
    sorted_tracks = sorted(tracks, key=lambda track: track['number'])
    for track in sorted_tracks:
        band = bc.band_info(track['band_id'])
        album = bc.album_info(track['album_id'])
        art = track.get('large_art_url',album['large_art_url'])
        listitem=xbmcgui.ListItem(str(track['number']) + ' - ' + track['title'], thumbnailImage=art, iconImage=art)
        listitem.setProperty('IsPlayable','true')
        infos = {
            'title':track['title'],
            'tracknumber':track['number'],
            'duration':track['duration'],
            'lyrics':track.get('lyrics',''),
            'album':album['title'],
            'artist':band['name']
            }
        listitem.setInfo('Music', infos)
        url=call_plugin_url(MODE_PLAY, {'track_id':track['track_id']})
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=listitem)
    xbmcplugin.endOfDirectory(handle=plugin_handle, succeeded=True)

def play_track(track):
    band = bc.band_info(track['band_id'])
    album = bc.album_info(track['album_id'])
    art = track.get('large_art_url',album['large_art_url'])
    li = xbmcgui.ListItem(label=track['title'], path=track['streaming_url'], thumbnailImage=art, iconImage=art)
    infos = {
        'title':track['title'],
        'tracknumber':track['number'],
        'duration':track['duration'],
        'lyrics':track.get('lyrics',''),
        'album':album['title'],
        'artist':band['name'],
        }
    li.setInfo("Music", infos)
    xbmcplugin.setResolvedUrl(handle=plugin_handle, succeeded=True, listitem=li)

def _show_keyboard(default="", heading="", hidden=False):
    ''' Show the keyboard and return the text entered. '''
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return unicode(keyboard.getText(), "utf-8")
    return default

if not os.path.isfile(keyFile):
    xbmcgui.Dialog().ok('Bandcamp', 'resources/data/key.txt not found, you need a bandcamp api key.', 'This shouldn\'t happen if you are just a user.', 'If so, contact me : pierre(at)lule(dot)fr')
    exit(0)

test = bc.set_and_test_key(open(keyFile,'r').read().rstrip())
if not test['success']:
    if test['error_message'] == 'bad key':
        xbmcgui.Dialog().ok('Bandcamp', 'Sorry, but Bandcamp refused the plugin key', 'This means that the Bandcamp addon isn\'t usable anymore.', 'Please contact me : pierre(at)lule(dot)fr to correct this.')
        exit(0)
    else:
        xbmcgui.Dialog().ok('Bandcamp', 'Error : '+test['error_message'], 'The addon might not work well', 'Please contact me if the problem persists : pierre(at)lule(dot)fr')

args = {}
mode = MODE_SEARCH
if plugin_arguments:
    args = urlparse.parse_qs(plugin_arguments)
    mode = args['mode'][0]

if mode == MODE_HOME:
    band_list(bc.search_band('amanda palmer'))
elif mode == MODE_BAND:
    album_list(bc.discography(args['band_id'][0]))
elif mode == MODE_ALBUM:
    track_list(bc.track_list(args['album_id'][0]))
elif mode == MODE_PLAY:
    if 'track_id' in args:
        play_track(bc.track_info(args['track_id'][0]))
    elif 'album_id' in args:
        print "play album, TODO"
elif mode == MODE_SEARCH:
    query = ''
    if not 'query' in args:
        query = _show_keyboard(heading='Band name')
    else:
        query = args['query'][0]
    band_list(bc.search_band(query))
else:
    band_list(bc.search_band('amanda palmer'))
