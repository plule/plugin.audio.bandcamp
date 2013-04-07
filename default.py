import datetime
from xbmcswift2 import Plugin
from xbmcswift2 import ListItem
from xbmcswift2 import xbmc, xbmcplugin
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
    if search_string == '':
        return None
    if search_string:
        url = plugin.url_for(
            endpoint='search',
            search_string=search_string
        )
        plugin.redirect(url)

@plugin.route('/search/<search_string>/<page>', name='search_page')
@plugin.route('/search/<search_string>/')
def search(search_string, page=0):
    page = int(page)
    givenpage = page
    if(page ==0):
        page = 1
    results,has_prev,has_next = bc.search(search_string, page)
    items = []
    for result in results:
        item_type = {'ARTIST':'band','ALBUM':'album','TRACK':'track'}.get(result['type'],None)
        label1 = result['name']
        label2 = item_type
        if result['genre']:
            label2 = label2 + ' - ' + result['genre']
        if result['by']:
            label2 = label2 + ' by ' + result['by']
        label2 = label2.strip()
        
        if label2 != '':
            label1 = u"{0} ({1})".format(label1, label2)

        li = ListItem(
            label = label1,
            label2 = label2,
            icon = result.get('art',None),
            thumbnail = result.get('art',None),
            path = plugin.url_for('show_url', url = result.get('url',None))
        )
        items.append(li)
    if has_prev:
        items.insert(0, {
            'label': '<< Previous',
            'path': plugin.url_for('search_page', search_string=search_string, page=str(page - 1))
        })
    if has_next:
        items.append({
            'label': 'Next >>',
            'path': plugin.url_for('search_page', search_string=search_string, page=str(page + 1))
        })
    plugin.add_sort_method(xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE, '%X')
    if(givenpage == 0):
        return plugin.finish(items, update_listing=False)
    else:
        return plugin.finish(items, update_listing=True)
        



@plugin.route('/band/<band_id>/')
def show_band(band_id):
    plugin.set_content('albums')
    band = bc.band_info(band_id)
    albums = bc.get_albums(band_id)
    album_items = [get_album_item(album, band) for album in albums]
    if len(bc.get_singles(band_id)) > 0:
        album_items.append({
            'label': 'Single tracks',
            'path' : plugin.url_for('show_band_singles', band_id=band_id)
        })
    return album_items

@plugin.route('/band/<band_id>/singles/')
def show_band_singles(band_id):
    plugin.set_content('songs')
    tracks = bc.get_singles(band_id)
    return [get_track_item(track) for track in tracks]

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
    if url_info.get('track_id',None):
        plugin.redirect(plugin.url_for('show_track', track_id = url_info['track_id']))
    elif url_info.get('album_id',None):
        plugin.redirect(plugin.url_for('show_album', album_id = url_info['album_id']))
    elif url_info.get('band_id',None):
        plugin.redirect(plugin.url_for('show_band', band_id = url_info['band_id']))

@plugin.route('/url/<url>/play_a_track/')
def play_url(url):
    try:
        url_info = bc.url_info(url)
    except:
        return None
    if url_info.get('track_id',None):
        plugin.redirect(plugin.url_for('play_track', track_id = url_info['track_id']))
    elif url_info.get('album_id',None):
        album = bc.album_info(url_info['album_id'])
        plugin.redirect(plugin.url_for('play_track', track_id = album['tracks'][0]['track_id']))
    elif url_info.get('band_id',None):
        discography = bc.discography(url_info['band_id'])
        if len(discography) == 0:
            return None
        first = discography[0]
        if url_info.get('track_id',None):
            plugin.redirect(plugin.url_for('play_track', track_id = first['track_id']))
        elif url_info.get('album_id',None):
            album = bc.album_info(first['album_id'])
            plugin.redirect(plugin.url_for('play_track', track_id = album['tracks'][0]['track_id']))
        return None

def get_band_item(band):
    name = band.get('name',None)
    domain = band.get('subdomain',None)
    li = ListItem(
        label = u"{0} ({1})".format(name, domain),
        path = plugin.url_for('show_band', band_id = band['band_id'])
    )
    return li

def get_album_item(album, band = None):
    if (not band) and (not album.get('artist',None)):
        band = bc.band_info(album['band_id'])

    year = year_from_timestamp(int(album['release_date']))
    artist = album.get('artist', band['name'])

    li = ListItem(
        label = u"{1} - {0}".format(album['title'], year),
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
        if track.get('album_id',None):
            album = bc.album_info(track['album_id'])
        else:album = {}

    if not band:
        band = bc.band_info(track['band_id'])

    art = track.get('large_art_url', album.get('large_art_url',None))
    release_date = track.get('release_date', album.get('release_date',None))
    artist = track.get('artist', album.get('artist', band['name']))
    if track.get('number',None):
        label = u"{0} - {1}".format(track['number'], track['title'])
    else: label = track['title']
    li = ListItem(
        label = label,
        icon=art,
        thumbnail=art,
        path=plugin.url_for('play_track', track_id = track['track_id']),
    )
    li.set_property('mimetype','audio/mpeg')
    li.set_is_playable(True)
    infos = {
        'title':track['title'],
        'tracknumber':track.get('number',None),
        'duration':track['duration'],
        'lyrics':track.get('lyrics',''),
        'album':album.get('title',None),
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
    try:
        return datetime.datetime.fromtimestamp(timestamp).year
    except:
        return None

if __name__ == '__main__':
    bc = Bandcamp(open(keyFile,'r').read().rstrip(), plugin)
    plugin.run()
