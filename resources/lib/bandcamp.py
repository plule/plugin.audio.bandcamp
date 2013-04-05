# -*- coding: utf-8 -*-

'''
@author: plule

Copyright (C) 2013 plule

This file is part of XBMC Bandcamp Plugin.

This file provides a simple python interface to bandcamp's api
'''

import urllib,urllib2
import simplejson as json
from xbmcswift2 import Module

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
    def __init__(self, key, plugin):
        self.key = key
        self.api = plugin
        self.bands = self.api.get_storage('bands', TTL = 60)
        self.discographies = self.api.get_storage('discographies', TTL = 60)
        self.albums = self.api.get_storage('albums', TTL = 60)
        self.tracks = self.api.get_storage('tracks', TTL = 60)
        
    def get_module(self):
        return self.api

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
        res = self.call_api(MOD_BAND, FUNC_SEARCH, {'name':name})['results']
        for band in res:
            self.bands[band['band_id']] = band #TODO : doesn't work ?
        return res

    def search_bands(self, names):
        return self.search_band(','.join(names)) #todo twelve max

    def isalbum(self, thing):
        return 'album_id' in thing

    def discography(self, band_id):
        band_id = int(band_id)
        if band_id in self.discographies:
            return self.discographies[band_id]
        self.discographies[band_id] = filter(self.isalbum, self.call_api(MOD_BAND, FUNC_DISCOGRAPHY, {'band_id':band_id})['discography']) #TODO : remove filter
        return self.discographies[band_id]

    def track_list(self, album_id):
        return call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})['tracks']

    def band_info(self, band_id):
        band_id = int(band_id)
        if band_id in self.bands:
            return self.bands[band_id]
        self.bands[band_id] = self.call_api(MOD_BAND, FUNC_INFO, {'band_id':band_id})
        return self.bands[band_id]

    def album_info(self, album_id):
        album_id = int(album_id)
        if album_id in self.albums:
            return self.albums[album_id]
        album = self.call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})
        self.albums[album_id] = album
        for track in album['tracks']:
            self.tracks[track['track_id']] = track
        return album

    def track_info(self, track_id):
        track_id = int(track_id)
        if track_id in self.tracks:
            return self.tracks[track_id]
        self.tracks[track_id] = self.call_api(MOD_TRACK, FUNC_INFO, {'track_id':track_id})
        return self.tracks[track_id]
