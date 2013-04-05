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
    item = {
        'label': 'Search',
        'path': plugin.url_for('show_search'),
    }
    return [item]

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
    bands = bc.search_band(search_string)
    plugin.set_content('artists')
    items = [{
            'label': band['name']+' ('+band['subdomain']+')',
            'path': plugin.url_for('show_band', band_id = band['band_id'])
            } for band in bands]
    return items

@plugin.route('/band/<band_id>/')
def show_band(band_id):
    band = bc.band_info(band_id)
    albums = bc.discography(band_id)
    plugin.set_content('albums')
    items = []
    for album in albums:
        year = datetime.datetime.fromtimestamp(int(album['release_date'])).year
        li = ListItem(
            label = '{1} - {0}'.format(album['title'], year),
            icon=album['large_art_url'],
            thumbnail=album['large_art_url'],
            path=plugin.url_for('show_album', album_id = album['album_id'])
            )
        infos = {
            'year':year,
            'album':album['title'],
            'artist':band['name']
            }
        li.set_info('Music', infos)
        items.append(li)
    return items

@plugin.route('/album/<album_id>/')
def show_album(album_id):
    plugin.set_content('songs')
    album = bc.album_info(album_id)
    band = bc.band_info(album['band_id'])
    items = []
    for track in album['tracks']:
        art = track.get('large_art_url', album['large_art_url'])
        li = ListItem(
            label = '{0} - {1}'.format(track['number'], track['title']),
            icon=art,
            thumbnail=art,
            path=plugin.url_for('play', track_id = track['track_id'])
            )
        li.set_is_playable(True)
        infos = {
            'title':track['title'],
            'tracknumber':track['number'],
            'duration':track['duration'],
            'lyrics':track.get('lyrics',''),
            'album':album['title'],
            'artist':band['name']
            }
        li.set_info('Music', infos)
        items.append(li)
    return items

@plugin.route('/track/<track_id>/')
def play(track_id):
    track = bc.track_info(track_id)
    plugin.set_resolved_url(track['streaming_url'])

if __name__ == '__main__':
    bc = Bandcamp(open(keyFile,'r').read().rstrip(), plugin)
    plugin.run()
