#!/usr/bin/env python
import pymongo
import random
import time

DATABASE='musicdb'
CURRENT_SONG_COLLECTION='currentSong'
HISTORY_COLLECTION='history'
QUEUE_COLLECTION='queue'
TRACKS_COLLECTION='tracks'
ARTISTS_COLLECTION='artists'
HISTORY_EXPIRES_IN=14400 # seconds

def ices_init():
	conn = None
	try: conn = pymongo.Connection()
	except: 
		print "Can't initialize MongoDB connection"
		return 0

	history = conn[DATABASE][HISTORY_COLLECTION]
	history.ensure_index([('timestamp', pymongo.DESCENDING)])
	return 1

def ices_shutdown():
	print "Shutting down python..."

def ices_get_next():
	
	# taking the song from queue
	song = getQueuedSong()
	if not song is None:
		storeCurrentSong(song)
		return song['file'].encode('utf-8')

	# there's no queued songs, taking a random one	
	currentSong = getCurrentSong()
	if currentSong is None:
		song = getRandomSong()
		storeCurrentSong(song)
		return song['file'].encode('utf-8')

	tries = 10
	while(tries > 0):
		song = getRandomSong()
		if not getHistoryContainsSong(song):
			storeCurrentSong(song)
			return song['file'].encode('utf-8')
		tries -= 1
	storeCurrentSong(song)
	return song['file'].encode('utf-8')

def ices_get_metadata():
	currentSong = getCurrentSong()
	if currentSong is None: return None
	meta = currentSong['artist'] + ' - ' + currentSong['title']
	if 'album' in currentSong.keys(): meta += ' // from "' + currentSong['album'] + '"'
	if 'year' in currentSong.keys(): meta += ' (' + currentSong['year'] + ')'
	if 'ordered_by' in currentSong.keys(): meta += ' ordered by ' +  currentSong['ordered_by']
	return meta.encode('utf-8')

def getHistoryContainsSong(songDoc):
	conn = pymongo.Connection()
	db = conn[DATABASE]
	history = db[HISTORY_COLLECTION]
	match = history.find_one({ 'artist' :  songDoc['artist'], 'title' : songDoc['title'] })
	return not match is None

def getCurrentSong():
	conn = pymongo.Connection()
	db = conn[DATABASE]
	currentSong = db[CURRENT_SONG_COLLECTION].find_one()
	return currentSong

def storeCurrentSong(songDoc):
	conn = pymongo.Connection()
	db = conn[DATABASE]
	db[CURRENT_SONG_COLLECTION].drop()
	db[CURRENT_SONG_COLLECTION].insert(songDoc)
	history = db[HISTORY_COLLECTION]
	hsong = songDoc.copy()
	hsong.update({'timestamp' : int(time.time())})
	history.insert(hsong)
	cleanHistory()
	return songDoc

def cleanHistory():
	expire_ts = int(time.time() - HISTORY_EXPIRES_IN)
	conn = pymongo.Connection()
	db = conn[DATABASE]
	history = db[HISTORY_COLLECTION]
	history.remove({'timestamp' : { '$lt' : expire_ts }})

def getQueuedSong():
	conn = pymongo.Connection()
	queue = conn[DATABASE][QUEUE_COLLECTION]
	song = queue.find_one()
	if song is None: return None

	queue.remove({ '_id' : song['_id'] })
	return song

def getRandomSong():
	conn = pymongo.Connection()
	db = conn[DATABASE]
	tracks = db[TRACKS_COLLECTION]
	artists = db[ARTISTS_COLLECTION]

	# Getting random artist. Not the one who is playing now
	ac = artists.count()
	currentSong = getCurrentSong()
	artist = None
	
	if currentSong is None or ac < 2:
		ind = random.randint(0, ac-1)
		artist = artists.find_one(skip=ind)
	else:
		ind = random.randint(0, ac-2)
		artist = artists.find_one({'name' : { '$ne' : currentSong['artist'] }}, skip=ind)

	trackcount = tracks.find({'artist' :  artist['name']}).count()
	ind = random.randint(0, trackcount-1)
	song = tracks.find_one({'artist' : artist['name']}, skip=ind)
	return song
