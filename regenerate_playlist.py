#!/usr/bin/env python

import pymongo
import os
import sys
import eyeD3
from mp3utils import *

DEFAULT_MUSIC_DIRECTORY='/usr/share/icecast2/music'
DATABASE='musicdb'
COLLECTION='tracks'
TMP_COLLECTION='tracks_tmp'
ARTISTS_COLLECTION='artists'
ALBUMS_COLLECTION='albums'

music_dir = DEFAULT_MUSIC_DIRECTORY
if len(sys.argv) > 1:
  music_dir = sys.argv[1]
files = get_mp3_files(music_dir)
count = 0
tags = []
artists = {}
albums = {}

conn = pymongo.Connection()
db = conn[DATABASE]
coll = db[TMP_COLLECTION]
coll.drop()
tag = eyeD3.Tag()

for f in files:
  
  if tag.link(f) != 1:
    print "Can not read tags from file " + f
    continue
  
  info = { 'file' : f, 'num' : count }
  if not tag.getAlbum() is None: info['album'] = format_tag(tag.getAlbum())
  if not tag.getYear() is None: info['year'] = tag.getYear()
  info['title'] = tag.getTitle()
  info['artist'] = tag.getArtist()
  
  info['title'] = format_tag(info['title'])
  info['artist'] = format_tag(info['artist'])

  info['tracknum'] = tag.getTrackNum()[0]
  
  if not info['artist'] in artists.keys():
    artists[info['artist']] = 1
  else:
    artists[info['artist']] += 1
  
  if 'year' in info.keys():
    year = info['year']
  else:
    year = None

  if not info['artist'] in albums.keys():
    albums[info['artist']] = {}
  albums[info['artist']][info['album']] = year
  coll.insert(info)
  
  count+=1

artists_collection = db[ARTISTS_COLLECTION]
artists_collection.drop()
for artist in artists.keys():
  artists_collection.insert({ 'name' : artist, 'songs' : artists[artist] })
artists_collection.ensure_index([('name', pymongo.ASCENDING)])

albums_collection = db[ALBUMS_COLLECTION]
albums_collection.drop()
for artist in albums.keys():
  for album in albums[artist].keys():
    year = albums[artist][album]
    albums_collection.insert({'artist' : artist, 'album' : album, 'year' : year })
albums_collection.ensure_index([('artist', pymongo.ASCENDING), ('album', pymongo.ASCENDING)])

coll.ensure_index([('artist', pymongo.ASCENDING), ('album', pymongo.ASCENDING), ('tracknum', pymongo.ASCENDING)])
coll.ensure_index([('num', pymongo.ASCENDING)])
coll.ensure_index([('file', pymongo.ASCENDING)])

db[COLLECTION].drop()
coll.rename(COLLECTION)
