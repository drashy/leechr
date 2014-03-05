#!/usr/bin/env python
#
# Leechr - <http://ashysoft.wordpress.com/>
#
#	Copyright 2008-2009 Paul Ashton
#
#	This file is part of Leechr.
#
#	Leechr is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	Leechr is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with Leechr.  If not, see <http://www.gnu.org/licenses/>.
#

SOURCE_DIR = ""	# The directory that your files are in to begin with
DEST_ROOT = "" # The dir that the DEST_DIRS are stored in

DEST_DIRS = {	"dir1":["word1", "word2", "word3"],
				"dir2":["word4", "word5"],
				"dir3":["word6"]
			}

import os, shutil

#Check some things..
if not SOURCE_DIR or not DEST_ROOT:
	exit("Fatal Error: SOURCE_DIR and/or DEST_ROOT are not set. Please edit this file and set them.")
if not os.access( SOURCE_DIR, os.W_OK ):
	exit("Fatal Error: '%s' is not writable or does not exist." % SOURCE_DIR)
for key in DEST_DIRS.keys():
	p = os.path.join(DEST_ROOT,key)
	if not os.access( p, os.W_OK ):
		exit("Fatal Error: '%s' is not writable or does not exist." % p)


print("Checking '%s'.." % SOURCE_DIR)
for item in os.listdir(SOURCE_DIR):
	if( os.path.isfile( os.path.join(SOURCE_DIR,item) ) ):
		moved = False
		for key in DEST_DIRS.keys():
			for word in DEST_DIRS[key]:
				if word.lower() in item.lower():
					src = os.path.join(SOURCE_DIR,item)
					dst = os.path.join(DEST_ROOT,key,item)
					print("Move '%s' to '%s'" % (src,dst))
					shutil.move(src, dst)
					moved = True
					break
			if moved:
				break
