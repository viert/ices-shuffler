#!/usr/bin/env python

import os

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

