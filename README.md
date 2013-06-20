ices-shuffler
=============

ices-shuffler is an ices0 python module to perform 'smart' shuffling.
It tries not to play two songs by one performer in a row and actually
it tries not to play the song already played as saved in history. 
Shuffler has own queue and it plays tracks from queue forcedly if it finds some.
ices-shuffler is written and used for playing shuffle at http://viert.fm/


Some explanations and architecture docs:

History cleans itself after a period of time (HISTORY_EXPIRES_IN const)
so tracks removed from history can be played again.

Anything is stored in mongodb. Mongodb collections are described below:

==tracks

Used to store all tracks shuffler can play. For example

> db.tracks.findOne()
{
  "_id" : ObjectId("5002bf859e34f450a6000000"),
  "album" : "Whitesnake",
  "title" : "Bad Boys",
  "artist" : "Whitesnake",
  "tracknum" : 2,
  "num" : 0,
  "file" : "/usr/share/icecast2/music/Whitesnake/1987 - Whitesnake/(02) [Whitesnake] Bad Boys.mp3",
  "year" : "1987"
}

==artists

Stores the artists of the tracks.

> db.artists.findOne()
{
  "_id" : ObjectId("5002bf969e34f450a600041c"),
  "name" : "Steve Vai",
  "songs" : 25
}

==albums

Stores all the albums

> db.albums.findOne()
{
  "_id" : ObjectId("5002bf969e34f450a6000435"),
  "album" : "Alien Love Secrets",
  "year" : "1995",
  "artist" : "Steve Vai"
}

==queue

Stores queue. Format of data is the same with 'tracks' collection. So to put the song
in queue you have to copy its document from tracks to queue collection.

==history

Just like queue it stores track documents this time the ones already played.



This repo contains some useful scripts to help you create tracks/albums/artists collections

inspect_tracks.py [dir] 
  
  inspects tracks in dir, extracts mp3 tags and shows
  documents it is ready to put to mongodb. This is useful when you have mp3 tracks
  with broken tags or non-unicode tags. If you inspected files and find out everything
  is ok, you can run

regenerate_playlist.py [dir]

  it inspects files in dir and stores everything it finds to mongodb collections.
