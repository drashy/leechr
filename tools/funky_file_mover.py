#!/usr/bin/env python
#
# Leechr - <http://ashysoft.wordpress.com/>
#
#  Copyright 2008-2009 Paul Ashton <drashy@gmail.com>
#
#  This file is part of Leechr.
#
#  Leechr is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Leechr is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Leechr.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import shutil

HOLDING_DIR = "/jail/glftpd/site/TV3/new/"  # The directory that your downloads are in
DEST_DIR = "/jail/glftpd/site/TV3/new/"    # The directory where you want your .avi/.mkv files moved to
DIR_STARTWITH = "NEW_TODAY-" # Directory MUST start with this

VALID_FILES = [".avi", ".mkv"]  # Files with these extensions will be moved to DEST_DIR
IGNORE_LIST = ["sample"]    # but not if they contain these words
DELETE_PROCESSED_DIRS = True  # Delete the directory (and any files left in it) once we have moved the files we want out of it

#Check some things..
if not HOLDING_DIR or not DEST_DIR:
  exit("Fatal Error: HOLDING_DIR and/or DEST_DIR are not set. Please edit %s and set them." % __file__)
if not os.access( HOLDING_DIR, os.W_OK ):
  exit("Fatal Error: HOLDING_DIR '%s' is not writable." % HOLDING_DIR)
if not os.access( DEST_DIR, os.W_OK ):
  exit("Fatal Error: DEST_DIR '%s' is not writable." % DEST_DIR)

# Get all dirs in holding dir..
dirList = []
print("Checking '%s'.." % HOLDING_DIR)
for directory in os.listdir(HOLDING_DIR):
  if( os.path.isdir( os.path.join(HOLDING_DIR,directory) ) ):
    if len(DIR_STARTWITH)>0:
      if directory.find(DIR_STARTWITH) == 0:
        dirList.append(directory)
    else:
      dirList.append(directory)

if( len(dirList) < 1 ):
  print("Nothing to move.")
  exit()

# Check each dir in list for valid files..
for directory in dirList:
  for item in os.listdir( os.path.join(HOLDING_DIR, directory) ):
    # Check if item should be ignored or not..
    b = False
    for word in IGNORE_LIST:
      if word in item:
        b = True
    if b:
      continue
    
    # Check for files to move..
    name, ext = os.path.splitext(item)
    if ext in VALID_FILES:
      source = os.path.join(HOLDING_DIR, directory, item)
      dest = os.path.join(DEST_DIR, item)
      
      # Move the file..
      print("Move '%s' to '%s'" % (source, dest))
      shutil.move(source, dest)
      
  # Delete the original dir..
  if DELETE_PROCESSED_DIRS:
    sourceDir = os.path.join(HOLDING_DIR, directory)
    print("Delete '%s'" % sourceDir)
    shutil.rmtree( sourceDir )
      
exit("Done!")
