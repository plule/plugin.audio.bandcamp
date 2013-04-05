# -*- coding: utf-8 -*-

'''
@author: plule

Copyright (C) 2013 plule

This file is part of XBMC Bandcamp Plugin.

This file provides a simple python interface to bandcamp's api
'''

import urllib,urllib2
import simplejson as json

URL_API_BASE='http://api.bandcamp.com/api/'

# Modules
MOD_BAND='band/'
MOD_ALBUM='album/'
MOD_TRACK='track/'
MOD_URL='url/'

# Functions
FUNC_SEARCH='search'
FUNC_DISCOGRAPHY='discography'
FUNC_INFO='info'

# Actions
ACTIONS={
    1:'download',
    2:'buy'
    }

URL_API_VERSIONS={
    MOD_BAND:'3/',
    MOD_ALBUM:'2/',
    MOD_TRACK:'3/',
    MOD_TRACK:'1/'
    }

class KeyError(Exception):
    pass

class ApiError(Exception):
    pass

class Bandcamp():
    def __init__(self, key):
        self.key = key

#band_cache = keydefaultdict(
#    lambda band_id:call_api(MOD_BAND, FUNC_INFO, {'band_id':band_id}))
#album_cache = keydefaultdict(
#    lambda album_id: call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id}))
#track_cache = keydefaultdict(
#    lambda track_id: call_api(MOD_TRACK, FUNC_INFO, {'track_id':track_id}))

    def call_api(self, module, function, params):
        url = URL_API_BASE + module + URL_API_VERSIONS[module] + function + '?' + 'key=' + self.key + '&' + urllib.urlencode(params)
        print 'CALLING...........'+url
        ret = json.loads(urllib2.urlopen(url).read())
        if('error' in ret):
            if(ret['error_message'] == 'bad key'):
                raise KeyError()
            else:
                raise ApiError()
        return json.loads(urllib2.urlopen(url).read())

    def search_band(self, name):
        return self.call_api(MOD_BAND, FUNC_SEARCH, {'name':name})['results']

    def search_bands(self, names):
        return self.search_band(','.join(names)) #todo twelve max

    def isalbum(self, thing):
        return 'album_id' in thing

    def discography(self, bandid):
        return filter(self.isalbum, self.call_api(MOD_BAND, FUNC_DISCOGRAPHY, {'band_id':band_id})['discography']) #TODO : remove filter

    def track_list(self, album_id):
        return call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})['tracks']

    def band_info(self, band_id):
        return call_api(MOD_BAND, FUNC_INFO, {'band_id':band_id})

    def album_info(self, album_id):
        album = call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})
        return album

    def track_info(self, track_id):
        return call_api(MOD_TRACK, FUNC_INFO, {'track_id':track_id})
