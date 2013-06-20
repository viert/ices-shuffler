#!/usr/bin/env python

import os
import sys
import eyeD3

DEFAULT_MUSIC_DIRECTORY='.'

def get_mp3_files(dirname):
  results = []
  for root, dirnames, filenames in os.walk(dirname):
    for filename in filenames:
      ext_index = 0
      try: ext_index = len(filename) - filename.index(".mp3")
      except: next
      if ext_index == 4:
        results.append(os.path.join(root, filename))
  return results

def format_tag(str):
  return str.title()

music_dir = DEFAULT_MUSIC_DIRECTORY
if len(sys.argv) > 1:
  music_dir = sys.argv[1]

files = get_mp3_files(music_dir)
tags = []
tag = eyeD3.Tag()

for f in files:
  
  if tag.link(f) != 1:
    print "Can not read tags from file " + f
    continue
  
  info = { 'file' : f }
  if not tag.getAlbum() is None: info['album'] = format_tag(tag.getAlbum())
  if not tag.getYear() is None: info['year'] = tag.getYear()
  info['title'] = tag.getTitle()
  info['artist'] = tag.getArtist()
  
  info['title'] = format_tag(info['title'])
  info['artist'] = format_tag(info['artist'])

  info['tracknum'] = tag.getTrackNum()[0]
  
  print str(info)

