# -*- coding: utf-8 -*-

'''
@author: plule

Copyright (C) 2013 plule

This file is part of XBMC Bandcamp Plugin.

This file provides a simple python interface to bandcamp's api
'''


import urllib,urllib2
import simplejson as json
from collections import defaultdict

class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret
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
api_key = {}
api_key['val']='unset'

URL_API_VERSIONS={
    MOD_BAND:'3/',
    MOD_ALBUM:'2/',
    MOD_TRACK:'3/',
    MOD_TRACK:'1/'
    }

def set_and_test_key(key):
    api_key['val']=key
    test_api = call_api(MOD_BAND, FUNC_SEARCH, {'name':'test'})
    if 'error' in test_api:
        return {'success':False, 'error_message':test_api['error_message']}
    return {'success':True}

#band_cache = keydefaultdict(
#    lambda band_id:call_api(MOD_BAND, FUNC_INFO, {'band_id':band_id}))
#album_cache = keydefaultdict(
#    lambda album_id: call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id}))
#track_cache = keydefaultdict(
#    lambda track_id: call_api(MOD_TRACK, FUNC_INFO, {'track_id':track_id}))

def call_api(module, function, params):
    url = URL_API_BASE + module + URL_API_VERSIONS[module] + function + '?' + 'key=' + api_key['val'] + '&' + urllib.urlencode(params)
    print 'CALLING...........'+url
    return json.loads(urllib2.urlopen(url).read())

def search_band(name):
    return call_api(MOD_BAND, FUNC_SEARCH, {'name':name})['results']

def search_bands(names):
    return search_band(','.join(names)) #todo twelve max

def isalbum(thing):
    return 'album_id' in thing

def discography(band_id):
    return filter(isalbum, call_api(MOD_BAND, FUNC_DISCOGRAPHY, {'band_id':band_id})['discography']) #TODO : remove filter

def track_list(album_id):
    return call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})['tracks']

def band_info(band_id):
    return call_api(MOD_BAND, FUNC_INFO, {'band_id':band_id})

'''def band_infos(band_ids):
    cached = {}
    batch = []
    batched = {}
    for band_id in band_ids:
        if band_id in band_cache:
            cached[band_id] = band_cache[band_id]
        else:
            batch.append(band_id)
    if len(batch) > 0:
        batched = call_api(MOD_BAND, FUNC_INFO, {'band_id':','.join(batch)})
        band_cache.update(batched)
    return dict(cached.item()+batched.item())'''

def album_info(album_id):
    album = call_api(MOD_ALBUM, FUNC_INFO, {'album_id':album_id})
    return album
'''    album = album_cache[album_id]
    for track in album['tracks']:
        track_cache[track['track_id']] = track
    return album'''

def track_info(track_id): # manually cached because the album api gives also tracks info
    return call_api(MOD_TRACK, FUNC_INFO, {'track_id':track_id})
#    return track_cache[track_id]

'''def track_infos(track_ids):
    cached = {}
    batch = []
    batched = {}
    for track_id in track_ids:
        if track_id in track_cache:
            cached['track_'+str(track_id)] = track_cache['track_'+str(track_id)]
        else:
            batch.append(track_id)
    if(len(batch) > 0):
        batched = call_api(MOD_TRACK, FUNC_INFO, {'track_id':','.join(batch)})
        track_cache.update(batched)
    return dict(cached.item()+batched.item())
'''
