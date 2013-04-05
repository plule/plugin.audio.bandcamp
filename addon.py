from xbmcswift2 import Plugin
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
            'path': plugin.url_for('show_band', 'band_id' = band['band_id'])
            } for band in bands]
    return items

@plugin.route('/band/<band_id>/')
def show_band(band_id):
    albums = bc.discography(band_id)
    plugin.set_content('albums')
    return []

if __name__ == '__main__':
    bc = Bandcamp(open(keyFile,'r').read().rstrip())
    print bc.search_band('brad hamers')
    plugin.run()
