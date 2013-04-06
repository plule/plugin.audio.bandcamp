import sys,time,datetime
from xbmcswift2 import Plugin,Module
from xbmcswift2 import ListItem
from xbmcswift2 import xbmc, xbmcgui
import os
from resources.lib.bandcamp import Bandcamp

plugin = Plugin('bandcamp')
baseDir = plugin.addon.getAddonInfo('path')

resDir = xbmc.translatePath(os.path.join(baseDir, 'resources'))
libDir = xbmc.translatePath(os.path.join(resDir,  'lib'))
datDir=  xbmc.translatePath(os.path.join(resDir,  'data'))
keyFile = xbmc.translatePath(os.path.join(datDir, 'key.txt'))

@plugin.route('/')
def index():
    button = xbmcgui.ControlButton(10,10,20,20, "hello")
    items = [{
        'label': 'Search',
        'path': plugin.url_for('show_search'),
    },{
        'label': 'cults band',
        'path': plugin.url_for('play_url', url='cults.bandcamp.com'),
        'is_playable': True
    },{
        'label': 'spiderwebbed album',
        'path': plugin.url_for('play_url', url='http://stumbleine.bandcamp.com/album/spiderwebbed'),
        'is_playable': True
    },{
        'label': 'glacier track',
        'path': plugin.url_for('play_url', url='http://stumbleine.bandcamp.com/track/glacier'),
        'is_playable': True
    }]
    return items

@plugin.route('/search/')
def show_search():
    search_string = plugin.keyboard(heading='Search')
    if search_string:
        url = plugin.url_for(
            endpoint='search',
            search_string=search_string
            )
        plugin.redirect(url)

@plugin.route('/search/<search_string>/')
def search(search_string):
    plugin.set_content('artists')
    bands = bc.search_band(search_string)
    return [get_band_item(band) for band in bands]

@plugin.route('/band/<band_id>/')
def show_band(band_id):
    plugin.set_content('albums')
    band = bc.band_info(band_id)
    albums = bc.discography(band_id)
    return [get_album_item(album, band) for album in albums]

@plugin.route('/album/<album_id>/')
def show_album(album_id):
    plugin.set_content('songs')
    return get_album_tracks(album_id)

@plugin.route('/album/<album_id>/play/')
def play_album(album_id):
    plugin.set_content('songs')
    tracks = get_album_tracks(album_id)
    plugin.add_to_playlist(tracks, 'music')

@plugin.route('/track/<track_id>/')
def show_track(track_id):
    plugin.set_content('songs')
    track = bc.track_info(track_id)
    return [get_track_item(track)]

@plugin.route('/track/<track_id>/play/')
def play_track(track_id):
    track = bc.track_info(track_id)
    plugin.set_resolved_url(track['streaming_url'])

@plugin.route('/url/<url>/')
def show_url(url):
    url_info = bc.url_info(url)
    if 'track_id' in url_info:
        plugin.redirect(plugin.url_for('show_track', track_id = url_info['track_id']))
    elif 'album_id' in url_info:
        plugin.redirect(plugin.url_for('show_album', album_id = url_info['album_id']))
    elif 'band_id' in url_info:
        plugin.redirect(plugin.url_for('show_band', band_id = url_info['band_id']))

@plugin.route('/url/<url>/play/')
def play_url(url):
    url_info = bc.url_info(url)
    if 'track_id' in url_info:
        plugin.redirect(plugin.url_for('play_track', track_id = url_info['track_id']))
    elif 'album_id' in url_info:
        plugin.redirect(plugin.url_for('show_album', album_id = url_info['album_id']))
    elif 'band_id' in url_info:
        plugin.redirect(plugin.url_for('show_band', band_id = url_info['band_id']))

def get_band_item(band):
    li = ListItem(
        label = '{0} ({1})'.format(band['name'], band['subdomain']),
        path = plugin.url_for('show_band', band_id = band['band_id'])
    )
    return li
    items = [{
        'label': band['name']+' ('+band['subdomain']+')',
        'path': plugin.url_for('show_band', band_id = band['band_id'])
    } for band in bands]

def get_album_item(album, band = None):
    if (not band) and (not 'artist' in album):
        band = bc.band_info(album['band_id'])

    year = year_from_timestamp(int(album['release_date']))
    artist = album.get('artist', band['name'])

    li = ListItem(
        label = '{1} - {0}'.format(album['title'], year),
        icon=album['large_art_url'],
        thumbnail=album['large_art_url'],
        path=plugin.url_for('show_album', album_id = album['album_id'])
    )
    infos = {
        'year':year,
        'album':album['title'],
        'artist':artist
    }
    li.set_info('Music', infos)
    return li


def get_track_item(track, album = None, band = None):
    if not album:
        album = bc.album_info(track['album_id'])
    if not band:
        band = bc.band_info(track['band_id'])

    art = track.get('large_art_url', album['large_art_url'])
    release_date = int(track.get('release_date', album['release_date']))
    artist = track.get('artist', album.get('artist', band['name']))

    li = ListItem(
        label = '{0} - {1}'.format(track['number'], track['title']),
        icon=art,
        thumbnail=art,
        path=plugin.url_for('play_track', track_id = track['track_id']),
    )
    li.set_property('mimetype','audio/mpeg')
    li.set_is_playable(True)
    infos = {
        'title':track['title'],
        'tracknumber':track['number'],
        'duration':track['duration'],
        'lyrics':track.get('lyrics',''),
        'album':album['title'],
        'artist':artist,
        'year':year_from_timestamp(release_date)
    }
    li.set_info('Music', infos)
    return li

def get_album_tracks(album_id):
    album = bc.album_info(album_id)
    band = bc.band_info(album['band_id'])
    return [get_track_item(track, album, band) for track in album['tracks']]

def year_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).year

if __name__ == '__main__':
    bc = Bandcamp(open(keyFile,'r').read().rstrip(), plugin)
    plugin.run()
