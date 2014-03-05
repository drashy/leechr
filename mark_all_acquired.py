#!/usr/bin/env python
# coding: utf-8
#
# Leechr - <http://ashysoft.wordpress.com/>
#
#  Copyright 2008-2014 Paul Ashton
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
import socket, sys, os, re, time, md5, urllib, urllib2
from BeautifulSoup import BeautifulStoneSoup

RETRY_TIME = 60 # Don't set below 30

# Default Config (don't change these, change the ones in leechr.conf)
ME_USERNAME = ""
ME_PASSWORD = ""


########################################################################
# F U N C T I O N S
########################################################################
def printl( text ):
  print(text.encode('utf-8'))
  return True



def openURL( url ):
  """ Open an url and return it """
  try:
    data = urllib2.urlopen( url )
  except urllib2.HTTPError, e:
    printl("HTTP Error: %s" % e.code)
    return False
  except urllib2.URLError, e:
    printl("URL Error: %s" % e.reason)
    return False
  return data



def decodeHTML( html ):
  """ Decode any HTML entities """
  return unicode(BeautifulStoneSoup(html,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))




def getEpisodeInfo():
  """ Get episode info from myepisodes.com """
  while True:
    printl("Requesting episode information from myepisodes.com...")
    page = openURL(ME_RSS_URL)
    if not page:
      printl("Error: Could not contact myepisodes.com, retrying in %s seconds.." % RETRY_TIME)
      time.sleep(RETRY_TIME)
    else:
      break

  xml = BeautifulStoneSoup( page )
  items = xml("item")
  if not items:
    printl("Fatal Error: Invalid XML, Please check your MyEpisodes Username and Password are correct")
    exit()

  toGrab = []
  for item in items:
    # Theres no eps to get so break
    if item.title.string == "No Episodes":
      break

    # Split up the stupid string into usable chunks
    tmp = re.findall("\[ (.[^\[\]]*) \]", decodeHTML(item.title.string))

    # Add to the list..
    toGrab.append(tmp)

  return toGrab






########################################################################
# C L A S S E S
########################################################################
class MyEpisodes(object):
  """ myepisodes.com stuff """
  ####################################################################
  # R E T R I E V E   S H O W   I D S
  ####################################################################
  def retrieveShowIDs(self):
    """ Load the show-id list from myeps """
    printl("Downloading show IDs from myepisodes.com..")

    # Open the 'manage shows' page..
    url = "http://www.myepisodes.com/shows.php?type=manage"
    try:
      page = urllib2.urlopen(url).read()
    except:
      printl("Error opening URL to get show IDs")
      exit()

    # Find all shows and their IDs..
    shows = {}
    showids = re.findall("<option value=\"(\d*)\">(.*[^<])</option>", page.decode("utf-8"))
    if showids:
      #make a nice dictionary
      for show in showids:
        shows[show[1]] = show[0]
    else:
      printl("Could not find any show IDs")
      exit()

    # Write them to the showid file
    try:
      f = open("showids.dat","w")
      if f:
        f.write(str(shows))
        f.close()
        printl("Wrote Show ID list to showids.dat")
    except:
      printl("Could not save showids.dat for writing")
      exit()

    return shows



  ####################################################################
  # L O A D   S H O W   I D S
  ####################################################################
  def loadShowIDs(self):
    """ Load the show-id list from file """
    try:
      f = open("showids.dat","r")
    except:
      return self.retrieveShowIDs()

    if f:
      data = eval(f.read())
      f.close()
      return data
    return False


  ####################################################################
  # L O G I N
  ####################################################################
  def login(self):
    """ Login to myeps """
    url = "http://www.myepisodes.com/login.php"
    data = urllib.urlencode({"username":self.username, "password":self.password, "u":"views.php", "action":"Login"})
    req = urllib2.Request(url, data)
    try:
      page = urllib2.urlopen(req).read()
    except:
      printl("Error logging in to myepisodes.com")
      exit()
    return True


  ####################################################################
  # I N I T
  ####################################################################
  def __init__(self, username, password):
    """ Init stuff """
    # Cookie catcher..
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(self.opener)

    # Show IDs
    self.showlist = {}

    # User/Pass
    self.username = username
    self.password = password

    # Login :)
    self.login()


  ####################################################################
  # G E T   S H O W   I D
  ####################################################################
  def getShowID(self, show):
    """ Convert a show name to an ID """
    if not self.showlist:
      self.showlist = self.loadShowIDs()

    if show in self.showlist:
      return self.showlist[show]
    else:
      # We could not find the ShowID in our local list so retrieve a new list and try again
      self.showlist = self.retrieveShowIDs()
      if show in self.showlist:
        return self.showlist[show]

    # We couldn't find the show at all
    return False


  ####################################################################
  # S E T   A C Q U I R E D
  ####################################################################
  def setAcquired(self, show, season, episode):
    """ Set an episode as acquired """
    #printl("Attempting to mark '%s S%sE%s' as acquired.." % (show,season,episode))
    ID = self.getShowID(show)
    S = int(season)
    E = int(episode)
    if not ID:
      printl("Error: Could not get ID for '%s'" % show)
      return False

    # Lets try to 'acquire' the show :)..
    url = "http://www.myepisodes.com/myshows.php?action=Update&showid=%s&season=%s&episode=%s&seen=0" % (ID, S, E)
    try:
      page = urllib2.urlopen(url) #.read()
    except:
      printl("Error opening URL to set show as acquired")
      return False

    # We did it!!  ..probably
    printl("Marked '%s S%sE%s' as acquired." % (show, season, episode))
    return True




########################################################################
# M A I N
########################################################################
print("******************************************************************************")
print("  WARNING:")
print("  You are about to mark *ALL* of your shows on myepisodes.com as 'Acquired'.")
print("******************************************************************************")
if raw_input("Are you SURE you want to do this? (Type yes to confirm): ").lower() != "yes":
  exit()

# Load config file..
CONFIG_FILE = "leechr.conf"
try:
    execfile(CONFIG_FILE)
except:
    printl("Fatal Error: Error reading %s" % CONFIG_FILE)
    exit()

# Sanity check..
if sys.version_info[:3] < (2,5) or sys.version_info[:3] >= (3,0):
  printl("Fatal Error: You need Python 2.5 or later (not 3.0) to use this script. You have v%s" % ver)
  exit()
if not ME_USERNAME or not ME_PASSWORD:
  printl("Fatal Error: You need to set your MyEpisodes.com Username and Password in %s" % CONFIG_FILE)
  exit()

ME_PASSWORDMD5 = md5.new(ME_PASSWORD).hexdigest()

# Define some URL's
ME_RSS_URL = "http://www.myepisodes.com/rss.php?feed=unacquired&uid="+ME_USERNAME+"&pwdmd5="+ME_PASSWORDMD5

# Set socket timeout
socket.setdefaulttimeout(30) # max time 30 seconds

# Login to myepisodes...
myeps = MyEpisodes(ME_USERNAME,ME_PASSWORD)


while 1:
  print("")
  toGrab = getEpisodeInfo()
  if not toGrab:
    printl("Nothing left to mark as acquired. All done :)")
    break

  showList = ""
  for show in toGrab:
    ep = "S"+show[1].replace("x","E")
    if not showList: showList = show[0] + " " + ep
    else: showList = showList + ", " + show[0] + " " + ep
  printl("%s shows to mark. (%s)\n" % (len(toGrab), showList))


  for i in toGrab:
    show, ep, date = i[0], "S"+i[1].replace("x","E"), i[3]
    showep = "%s %s" % (show, ep)

    # Tell myeps that we have acquired it..
    tmp = ep[1:].split("E")
    myeps.setAcquired(show, tmp[0], tmp[1])

printl("Bai!")
