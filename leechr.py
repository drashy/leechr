#!/usr/bin/env python
# coding: utf-8

# Leechr
# http://ashysoft.wordpress.com
#
# Copyright 2008-2014 Paul Ashton <drashy@gmail.com>
#
# This file is part of Leechr.
#
# Leechr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Leechr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Leechr.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import re
import sys
import urllib
import urllib2
import zipfile

DEBUG = False
LOGGING = False
RETRY_LIMIT = 2
RETRY_TIME = 5



def printl(text):
  """ Print to screen and save text to log file (if needed) """
  text = to_utf8(text)
  print(text)

  if LOGGING:
    fout = open(os.path.join(SCRIPTDIR, "leechr.log"), "a")
    if fout:
      fout.write(time.asctime() + ": " + text + "\n")
      fout.close()
  return True



def debug(text):
  """ Prints debug info """
  if not DEBUG:
    return False
  printl("# DEBUG: %s" % text)
  return True



def to_unicode(obj, encoding='utf-8'):
  if isinstance(obj, basestring):
    if not isinstance(obj, unicode):
      obj = unicode(obj, encoding)
  return obj



def to_utf8(obj, encoding='utf-8'):
  if isinstance(obj, basestring):
    if isinstance(obj, unicode):
      obj = obj.encode(encoding)
  return obj



def openURL(url):
  """ Open an url and return it """
  debug("Opening URL '%s'" % url)
  try:
    headers = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)", "Pragma":"no-cache", "Cache-Control":"no-cache"}
    req = urllib2.Request(url, None, headers)
    data = urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    printl("[!] HTTP Error: %s" % e.code)
    return False
  except urllib2.URLError, e:
    printl("[!] URL Error: %s" % e.reason)
    return False
  return data



def unpack_zip(filename, targetdir):
  """ Unzip filename to targetdir """
  # Open the zip
  zip = zipfile.ZipFile(filename, "r")
  if zip.testzip() != None:
    printl("[!] Error: Bad zip file")
    return False

  debug("ZIP Contents: %s" % zip.namelist())

  #Create DIRS first
  for f in zip.namelist():
    src = f[7:] # strip the "Leechr/" bit :)
    if src:
      if src.endswith("/"): # Its a directory
        dest = os.path.join(targetdir, src)
        if not os.access(dest, os.F_OK): # Doesn't exist already
          debug("\tDir '%s' doesn't exist, creating it.." % src)
          os.makedirs(dest)
        else:
          debug("\tDir '%s' exists." % src)

  #Extract files
  for f in zip.namelist():
    src = f[7:] # strip the "Leechr/" bit :)
    if src:
      if not src.endswith("/"): # Its a file
        dest = os.path.join(targetdir, src)
        debug("\tExtracting '%s' to '%s'.." % (src, dest))
        write_file(zip.read(f), dest)

  # Close zip file
  zip.close()
  return True



def download_leechr(version):
  """ Download and unpack new version of leechr """
  DOWNLOAD_URL = "http://leechr.googlecode.com/files/Leechr%s.zip" % version # http://leechr.googlecode.com/files/Leechr0.4.7.1.zip
  tmpfile = os.path.join(SCRIPTDIR,"update.zip")

  # Download new version to update.zip
  data = retrieve_url(DOWNLOAD_URL, "leechr update server")
  write_file(data, tmpfile)

  return tmpfile



def retrieve_url(url, friendly_name="server"):
  """ Download the url and return it """
  debug("retrieve_url '%s'" % url)
  for r in range(RETRY_LIMIT+1):
    h = openURL(url)
    if not h:
      if r+1 <= RETRY_LIMIT:
        printl("[!] Error: Could not contact %s, retrying in %s seconds.." % (friendly_name, RETRY_TIME))
        time.sleep(RETRY_TIME)
        printl("Retrying (attempt %s of %s)..." % (r+1, RETRY_LIMIT))
    else:
      break

  if not h:
    printl("[!] Error: Failed to contact %s after %s retries, giving up." % (friendly_name, RETRY_LIMIT))
    return False

  return h.read()



def check_for_updates_leechr():
  """ Check for updates to leechr """
  debug("Checking for updates to leechr..")
  try:
    page = openURL("http://code.google.com/p/leechr/downloads/list")
    if page:
      data = page.read()
      res = re.findall(r"Leechr([\d.]*\d)", data)
      res.sort(reverse=True)
      debug(res)
      latest = res[0]
      debug("latest=%s current=%s" %(latest,LEECHR_VERSION))

      lv = LEECHR_VERSION
      if " beta" in lv:
        lv = lv[:lv.find(' beta')]

      if latest > LEECHR_VERSION or (" beta" in LEECHR_VERSION and latest >= lv):
        filename = download_leechr(latest)
        unpack_zip(filename, SCRIPTDIR)
        if os.path.exists(filename):
          os.remove(filename) # delete update file
        printl("Downloaded new Leechr (v%s)" % latest)
      else:
        printl("Leechr is up to date (%s)" % LEECHR_VERSION)
  except:
    debug("[!] Failed to check for leechr updates (%s)" % str(sys.exc_info()))

  return False



def get_leechr_version():
  try:
    data = open(os.path.join(SCRIPTDIR, "main.py")).read()
    res = re.findall(r"LEECHR_VERSION = u[\"\'](.+?)[\"\']", data)
  except:
    return "0"
  if not res: return "0"
  return res[0]



def get_helpers_version():
  try:
    data = open(os.path.join(SCRIPTDIR, "helpers.dat")).read()
    res = re.findall("HELPERS_DAT_VERSION = (\d*)", data)
  except:
    return "0"
  if not res: return "0"
  return res[0]



def write_file(data, filename):
  """ Write the file data to disk """
  try:
    n = open(filename, "wb")  # TODO: Make sure theres not already a file by this name.
    n.write(data)
    n.close()
  except:
    return False

  return filename



def check_for_updates_helpers():
  """ Check for updates to helpers.dat """
  debug("Checking for updates to helpers.dat..")
  try:
    page = openURL("http://code.google.com/p/leechr/downloads/list").read()
    if not page:
      return False

    res = re.findall(r"helpers(\d+).dat", page)
    debug(res)
    if not res:
      debug("No helpers.dat found on google page")
      return False
    res.sort(reverse=True)
    latest = res[0]
    debug("latest=%s current=%s" % (latest, HELPERS_VERSION))
    if int(latest) > int(HELPERS_VERSION):
      data = retrieve_url("http://leechr.googlecode.com/files/helpers%s.dat" % latest, "leechr update server")
      if not data:
        printl("[!] Failed to download new 'helpers.dat' file.")
        return False
      write_file(data, os.path.join(SCRIPTDIR,"helpers.dat"))
      printl("Downloaded new 'helpers.dat' file.")
    else:
      printl("helpers.dat is up to date (%s)" % HELPERS_VERSION)
    return True
  except:
    debug("Failed to check for helpers.dat updates (%s)" % str(sys.exc_info()))
  return False



#########################################################################



SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

if not os.access(SCRIPTDIR, os.W_OK):
  printl("[!] Fatal Error: '%s' is not writable or does not exist." % SCRIPTDIR)
  exit()

LEECHR_VERSION = get_leechr_version()
HELPERS_VERSION = get_helpers_version()

printl("Checking for updates..")
check_for_updates_leechr()
check_for_updates_helpers()
printl("")
execfile(os.path.join(SCRIPTDIR,"main.py"))
