#!/usr/bin/env python
# coding: utf-8

# Leechr
# http://ashysoft.wordpress.com
#
# Copyright 2008-2015 Paul Ashton <drashy@gmail.com>
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

# With contributions from:
#    Rick Pass <rick.pass@gmail.com>
#    Stalksta
#    DaSchug
#                               ...Thanks guys :)

__author__ = "Paul Ashton (drashy@gmail.com)"
__version__ = "0.8"
__copyright__ = "Copyright (c) 2008-2015 Paul Ashton"
__license__ = "GNU GPL v3+"

import hashlib
import nntplibssl as nntplib
import os
import pickle
import random
import re
import socket
import struct
import sys
import time
import urllib
import urllib2
import zipfile
from datetime import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


# Defines
LEECHR_VERSION = u'0.8'
DEBUG = False

RETRY_TIME = 5 # don't want to flood search engines :)
RETRY_LIMIT = 2 # retry 2 times, if its still not working then the site is down and pointless to keep trying :)
MINIMUM_POST_SIZE = 100 # MB
MINIMUM_POST_SIZE_720P = 200 # MB
#ALLOWED_GROUPS = ["alt.binaries.tv", "alt.binaries.tvseries", "alt.binaries.multimedia", "alt.binaries.hdtv", "alt.binaries.hdtv.x264", "alt.binaries.teevee"]
BANNED_GROUPS = []
SEARCH_MODULES = ["LOCALNEWZNAB", "NZBCLUBCOM"]#, "NZBXCO", "NEWSHOSTCOZA", "SICKBEARDCOM", "NZBSORG", "NZBNDXCOM"]#, "NZBINDEXNL", "BINSEARCHINFO"] # In order of preference
SEARCH_MODULES_OFFLINE = []
EPISODE_FORMATS = ["S%.2dE%.2d", "%dx%.2d"]
EPISODE_TIMEOUTS = [] #[show_name, season_num, episode_num, attempts]
RETRIEVE_TIMES = {}
BAD_NZBS = {} # 'urlhash':'reason'
DMCA_REMOVED = []
DIDNT_FIND = []
LEECHR_STATS = {}
_PERSISTENT = ['BAD_NZBS', 'DMCA_REMOVED', 'RETRIEVE_TIMES', 'DIDNT_FIND', 'LEECHR_STATS']

# Default Config (don't change these, change the ones in leechr.conf)
USENET_USESSL = False
USENET_HOST = ""
USENET_PORT = 119
USENET_USERNAME = ""
USENET_PASSWORD = ""

ME_USERNAME = ""
ME_PASSWORD = ""

NZBSORG_APIKEY = ""
NZBNDXCOM_APIKEY = ""
USENETCRAWLERCOM_APIKEY = ""

LOCALNEWZNAB_URL = ""
LOCALNEWZNAB_APIKEY = ""

NZBDir = ""
NZB_SUBDIRS = False
NZBprefix = ""
NZBsuffix = ""
ME_RETRY = True
LOGGING = False
IGNORE_SHOWS = []
RETENTION_LIMIT = 0
FILESIZE_LIMIT = 5000
DAYS_EARLY = 2.0
DONT_STRIP_NZBS = False
NZB_UNWANTED_FILES = ["sample"]
AUTO_UPGRADE = True
IGNORE_EPISODES_OLDER_THAN = 0
GET_HD_VIDEO = True
SD_OVERRIDE = []
HD_OVERRIDE = []
TIMEOUT_DAYS = 6.0
TIMEOUT_ATTEMPTS = 0
AUTOMARK_ACQUIRE = True
USE_SCENE_NAMES = False
LOGDIR = ""


# Defaults for helpers.dat (don't change these, please report any
# changes and they will be incorporated into helpers.dat for everyone)
SEARCH_HELPERS = {}
LOCAL_FILTERS = {}
ALT_SHOW_NAMES = {}
BANNED_WORDS = []
SEASON_EP_SHIFT = {}
DAILY_SHOWS = []
NAMED_SHOWS = []
HELPERS_DAT_VERSION = 0
LEECHR_REQ_VERSION = "0"
REMATCH = {}
SD_SHOWS = []
HD_SHOWS = []


# Have a random Browser User Agent just incase :)
USERAGENT = random.choice(("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",
    "Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"))


########################################################################



def printl(text, wrap=True):
  """ Print to screen and save text to log file (if needed) """
  text = to_utf8(text)

  if not wrap and len(text)>80:
    text = "%s.." % text[:77]

  print(text)

  if LOGGING:
    fout = open(os.path.join(LOGDIR, "leechr.log"), "a")
    if fout:
      fout.write(time.asctime() + ": " + text + "\n")
      fout.close()
  return True


def debug(text):
  """ Prints debug info """
  if not DEBUG:
    return False

  import inspect
  caller = inspect.stack()[1][3]

  text = to_utf8(text)

  ts = time.strftime("%H:%M:%S", time.localtime()) + " (%s)" % caller

  # Multi-line output
  linelength = 145-len(ts)
  t = str(text)
  while(len(t)>linelength):
    printl("%s: %s..." % (ts, t[:linelength]))
    t = t[linelength:]
  else:
    printl("%s: %s" % (ts, t))

  fout = open(os.path.join(LOGDIR, "debug.log"), "a")
  if fout:
    fout.write("%s (%s): %s" % (ts, caller, to_utf8(text)))
    fout.close()
  return True



def getMyEpsAge(when):
  """ Calculate myepisodes age from date """
  if len(when) > 11:
    delta = datetime.now() - datetime.strptime(when, "%a-%d-%b-%Y") # Mon-09-Jul-2001
  else:
    delta = datetime.now() - datetime.strptime(when, "%d-%b-%Y") # "18-Feb-2008"

  return float("%.1f" % (delta.days + (delta.seconds / 86400.0))) # divide secs into days



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
  debug("Opening URL '%s' (%s)" % (url, USERAGENT))

  try:
    req = urllib2.Request(url, None, {"User-Agent":USERAGENT, "Pragma":"no-cache", "Cache-Control":"no-cache", 'Accept-encoding':'gzip'})
    response = urllib2.urlopen(req)

    # Check if gzipped..
    if response.info().get('Content-Encoding') == 'gzip':
      debug("gzipped content")
      from StringIO import StringIO
      import gzip
      buf = StringIO(response.read())
      data = gzip.GzipFile(fileobj=buf)
    else:
      debug("not gzipped content")
      data = response

  except urllib2.HTTPError, e:
    printl("[!] HTTP Error: %s" % e.code)
    return False
  except urllib2.URLError, e:
    printl("[!] URL Error: %s" % e.reason)
    return False
  except KeyboardInterrupt:
    raise
  except:
    printl("[!] Error: Unknown error while retrieving url")
    return False
  return data



def retrieve_url(url, friendly_name="server", retries=RETRY_LIMIT):
  """ Download the file at url and return it """
  debug("retrieve_url(): '%s'" % url)
  for retry in range(retries+1):
    h = openURL(url)
    if not h:
      if retry+1 <= retries:
        printl("[!] Error: Could not contact %s, retrying in %s seconds.." % (friendly_name, RETRY_TIME * (retry+1)))
        time.sleep(RETRY_TIME * (retry+1))
        printl("Retrying (attempt %s of %s)..." % (retry+1, retries))
    else:
      break

  if not h:
    printl("[!] Error: Failed to contact %s after %s retries, giving up." % (friendly_name, RETRY_LIMIT))
    return ''

  try:
    data = h.read()
  except:
    printl("[!] Error: Failed to read from %s." % friendly_name)
    return ''

  return data



def save_timeouts(data):
  """ Write the episode timeouts to timeout.dat """
  filename = os.path.join(SCRIPTDIR, "%s_timeout.dat" % ME_USERNAME.lower())
  try:
    f = open(filename, "wb")
    pickle.dump(data, f)
    f.close()
  except:
    debug("Couldn't save '%s'" % filename)
    return False
  debug("Wrote '%s'" % filename)
  return True



def load_timeouts():
  """ Read the episode timeouts from timeout.dat """
  filename = os.path.join(SCRIPTDIR, "%s_timeout.dat" % ME_USERNAME.lower())
  try:
    f = open(filename, "rb")
    data = pickle.load(f)
    f.close()
  except:
    debug("Couldn't load '%s'" % filename)
    return []
  debug("Loaded '%s'" % filename)
  return data



def write_file(data, filename, rename=True):
  """ Write the file data to disk """
  if not data:
    return False

  debug("About to write %s bytes to '%s'" % (len(data), filename))

  c = 1
  tmpfilename = filename
  if rename:
    while True:
      if not os.path.exists(tmpfilename):
        break;
      s = os.path.splitext(filename)
      tmpfilename = "%s (%s)%s" % (s[0], c, s[1])
      c=c+1

  try:
    n = open(tmpfilename, "wb")  # TODO: Make sure theres not already a file by this name.
    n.write(data)
    n.close()
  except:
    return False

  return tmpfilename



def nntpDownloadArticle(articleid):
  """ Download an article from usenet """
  debug("nntpDownloadArticle(): %s" % articleid)

  # Make sure we have our brackety things
  if articleid[:1] != '<':
    articleid = "<%s>" % articleid

  returnFalse = None
  nntp = None

  for retry in range(RETRY_LIMIT+1):
    data = False
    try:
      if USENET_USESSL:
        nntp = nntplib.NNTP_SSL(host=USENET_HOST, port=USENET_PORT, user=USENET_USERNAME, password=USENET_PASSWORD)
      else:
        nntp = nntplib.NNTP(host=USENET_HOST, port=USENET_PORT, user=USENET_USERNAME, password=USENET_PASSWORD)
      debug("nntp connected")
      data = nntp.article(articleid)
    except nntplib.NNTPTemporaryError:
      extype, exvalue = sys.exc_info()[:2]
      if "430 No such article" in exvalue:
        printl("[!] Error: No such article. Your news server does not have this article, it is probably too old, check your retention settings.")
      else:
        printl("[!] Error: Unexpected error grabbing article. %s" % exvalue)
      returnFalse = True
      break
    except KeyboardInterrupt:
      raise
    except:
      extype, exvalue = sys.exc_info()[:2]
      printl("[!] Error: Exception while grabbing article (%s (%s))" % (extype, exvalue))
      data = False

    if not data:
      if retry+1 <= RETRY_LIMIT:
        printl("[!] Error grabbing article: %s (%s), retrying in %s seconds.." % (extype, exvalue, RETRY_TIME*(retry+1)))
        time.sleep(RETRY_TIME*(retry+1))
        printl("Retrying (attempt %s of %s)..." % (retry+1, RETRY_LIMIT))
      else:
        printl("[!] Error grabbing article: %s (%s), giving up." % (extype, exvalue))
        returnFalse = True
        break
    else:
      break

  if data and " not found" in str(data[3]).lower():
    debug(str(data[3]))
    printl("[!] Warning: Empty article, it is probably too old, check your retention settings.")
    returnFalse = True

  try:
    if nntp:
      nntp.quit()
  except EOFError: #Seems this is produced when nntp.quit() is used.
    debug("Exception EOFError - Usenet connection closed (this appears to be normal)")
  except:
    extype, exvalue = sys.exc_info()[:2]
    debug("Unknown Exception (%s %s) while closing nntp connection." % (extype, exvalue))

  if returnFalse:
    return False

  return data[3]



#def yDecodeLine(line):
#  """ yDecode one line """
#  data = ""
#  pos = 0
#  while pos < len(line):
#    if line[pos] == "=": # Escape char
#      pos += 1
#      num = (ord(line[pos]) - 64 - 42) % 256
#    else:
#      num = (ord(line[pos]) - 42) % 256
#    data += chr(num)
#    pos += 1
#  return data



def yDecode(lines):
  """ Decode a yEnc encoded list """
  debug("yDecode() called with %s lines" % len(lines))
  decoded = ""
  linenum = 0
  ybegin = False
  while True:
    line = lines[linenum]
    if line[:8] == "=ybegin " and "line=" in line and "size=" in line and "name=" in line:
      ybegin = True
      obj = line.split()
      for o in obj:
        if "line=" in o: yline = o[5:]
        if "size=" in o: ysize = o[5:]
        if "name=" in o: yname = o[5:]
    elif line[:7] == "=ypart ":
      pass
    elif line[:6] == "=yend ":
      pass
    elif ybegin:
      data = ""
      pos = 0
      while pos < len(line):
        if line[pos] == "=": # Escape char
          pos += 1
          num = (ord(line[pos]) - 64 - 42) % 256
        else:
          num = (ord(line[pos]) - 42) % 256
        data += chr(num)
        pos += 1

      decoded += data
    else:
      pass

    linenum += 1
    if len(decoded) >= 5000: break;
    if linenum >= len(lines): break;

  debug("decoded data len: %s" % len(decoded))
  return decoded



def extractRarInfo(rardata):
  """ Grab filenames and file headers from within the rar data """
  if DEBUG:
    write_file(rardata, "debug.seg", rename=False)

  infos = []
  rarpos = 0
  while (rarpos+7 <= len(rardata)):
    HEAD_CRC, HEAD_TYPE, HEAD_FLAGS, HEAD_SIZE = struct.unpack("<HBHH", rardata[rarpos:rarpos+7])

    debug("HEAD_FLAGS='%s'" % HEAD_FLAGS)

    HEAD = rardata[rarpos:rarpos+HEAD_SIZE]
    rarpos += HEAD_SIZE

    if HEAD_TYPE == 0x74: # File Header Block
      PACK_SIZE, UNP_SIZE, HOST_OS, FILE_CRC, FTIME, UNP_VER, METHOD, NAME_SIZE, ATTR = struct.unpack("<IIBIIBBHI", HEAD[7:7+25])
      namepos = 32

      if METHOD != 0x30: #(0x30=STORED, 0x31-35=FASTEST-BEST)
        printl("[!] Warning: Compressed archive detected, Leechr can not check content.")

      # Skip zero-bytes, dunno why they're sometimes there (YET! anyone know?)
      while ord(HEAD[namepos])<2: # \x00 and \x01
        namepos += 1

      name = HEAD[namepos:namepos+NAME_SIZE]
      header, = struct.unpack("<I", rardata[rarpos:rarpos+4])
      infos.append((name,header))
      debug("Adding %s to infos" % str((name,header)))
      rarpos += PACK_SIZE # Seek past the file contents

  return infos



def xmlGetFirstArticle(data, text):
  """ Get the article name of the first segment of first file """
  for child in data:
    subject = child.get('subject')
    if subject and text in subject.lower():
      try:
        c = child.iter()
      except AttributeError: # .iter() doesn't exist in Python 2.6
        c = child.getiterator()
      except:
        pass

      for elem in c:
        if elem.get('number') == "1":
          return "<%s>" % elem.text



def check_for_passwords(nzbdata):
  """ Check NZB for passworded rar files """
  debug("check_for_passwords() called with %s bytes of data" % len(nzbdata))
  if DEBUG: write_file(nzbdata, "debug.nzb", rename=False)

  # Get root
  try:
    root = ET.fromstring(nzbdata)
  except ET.ParseError:
    error = "[!] Error: corrupt or incomplete NZB file"
    printl(error)
    return error
  except:
    error = "[!] Error parsing nzb, please report this and send in debug.nzb"
    write_file(nzbdata, "debug.nzb", rename=False)
    printl(error)
    return error

  # Find a 'first-file' .rar or .mkv
  for i in ['.part001.rar\"', '.part01.rar\"', '.mkv\"', '.avi\"', '.mp4\"', '.rar\"', '.r00\"']:
    seg = xmlGetFirstArticle(root, i)
    if seg:
      break

  # Couldn't find anything useful..
  if not seg:
    error = "Error finding first segment. Probably an incomplete nzb/post."
    printl("[!] %s " % error)
    return error

  debug("First segment of first-file is article %s" % seg)

  # Check if we already know DMCA killed this seg
  if seg in DMCA_REMOVED:
    error = "Article exterminated by DMCA :/"
    printl("[!] Previously checked. %s " % error)
    return error

  # Grab segment..
  debug("Grabbing %s..." % seg)
  segdata = nntpDownloadArticle(seg)
  if not segdata:
    error = "Error grabbing article, don't know why :/"
    printl("[!] %s " % error)
    return error

  #Check for DMCA take downs..
  if "DMCA" in ''.join(segdata):
    error = "Article exterminated by DMCA :/"
    printl("[!] %s " % error)
    DMCA_REMOVED.append(seg)
    return error

  # Check we have some yEncoded datas..
  if "=ybegin " not in ''.join(segdata):
    error = "Error grabbing article, not yencoded :/"
    printl("[!] %s " % error)
    return error

  # yDecode the data
  data = yDecode(segdata)

  names = []

  # Check the 4 byte checksum
  checksum, = struct.unpack("<I", data[:4])
  validFiles = {561144146:'rar', 2749318426L:'mkv', 1179011410:'avi', 335544320:'mp4', 402653184:'mp4'}
  if checksum in validFiles:
    debug("Found a .%s file" % validFiles[checksum])
    if validFiles[checksum] == 'rar':
      debug("Found a rar so lets check inside..")

      for item in extractRarInfo(data):
        debug("items: %s" % str(item))
        if item[1] in validFiles:
          debug("Found a .%s file (in rar)" % validFiles[item[1]])
          if validFiles[item[1]] == 'rar':
            printl("[!] Warning: RAR within a RAR is usually passworded, ignoring this NZB")
          else:
            names.append(item[0])
        else:
          debug("Unknown file: %s (%d) (in rar)" % item)
    else: #Not a rar
      debug("Plain %s file found, adding to names.." % validFiles[checksum].upper())
      names.append(validFiles[checksum])

  if not names:
    error = "[!] Error: No video files found."
    printl(error)
    return error

  #File seems ok..
  return False


def process_nzb(data, unwanted_files):
  """ Check NZB is ok and remove unwanted files """
  header = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n<!DOCTYPE nzb PUBLIC \"-//newzBin//DTD NZB 1.0//EN\" \"http://www.newzbin.com/DTD/nzb/nzb-1.0.dtd\">\n<!-- NZB fixed by Leechr -->\n<nzb xmlns=\"http://www.newzbin.com/DTD/2003/nzb\">\n"
  body = ""
  footer = "</nzb>\n"

  badcount = 0
  goodcount = 0
  bytes = 0

  xml = BeautifulStoneSoup(data)
  files = xml("file")

  for f in files:
    found = False
    name = f["subject"].lower()
    for unwanted in unwanted_files:
      if unwanted.lower() in name:
        found = unwanted.lower()
        break

    if not found:
      body = body + str(f) + "\n"
      goodcount += 1
    else:
      badcount += 1
      debug("Stripping unwanted file: %s (%s)" % (name, found))

  if goodcount < 1:
    printl("[!] Warning: Bad NZB, No files found.")
    return False

  if badcount > 0:
    printl("Stripped %s unwanted files from NZB." % badcount)

  return header + body + footer


def striphtmlentities(html):
  entities = {'&nbsp;':' ', '&quot;':'\'', '&lt;':'<', '&gt;':'>', '\t':'', '<strong>':'', '</strong>':''}
  for e in entities:
    html = html.replace(e, entities[e])
  return html

def decodeHTML(html):
  """ Decode any HTML entities (%gt; to > etc.)"""
  try:
    t = unicode(BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
  except:
    t = u""

  return t



def exitmsg(message):
  printl("")
  printl("---------------------------------------------------------------")
  printl(" %s" % message)
  printl(" If you find Leechr useful please consider buying me a beer :)")
  printl(" http://ashysoft.wordpress.com/donate")
  printl("---------------------------------------------------------------")



def getEpisodeInfo():
  """ Get episode info from myepisodes.com """
  page = retrieve_url("http://www.myepisodes.com/rss.php?feed=unacquired&uid="+ME_USERNAME+"&pwdmd5="+hashlib.md5(ME_PASSWORD).hexdigest(), "myepisodes.com")
  if not page:
    printl("[!] Fatal Error: Could not contact myepisodes.com, Leechr can not continue.")
    exit()

  xml = BeautifulStoneSoup(page)
  items = xml("item")
  if not items:
    printl("[!] Fatal Error: Bad response from myepisodes.com, Please check your MyEpisodes Username and Password are correct.")
    exit()

  episodes = []
  for item in items:
    # Theres no eps to get so break
    if item.title.string == "No Episodes":
      break

    # Split up the stupid string into usable chunks
    debug("item.title.string = '%s'" % decodeHTML(item.title.string))
    tmp = re.findall("\[ ?(.[^\[\]]*) \]", decodeHTML(item.title.string))
    debug("tmp = '%s'" % tmp)

    # get season and epi numbers
    tmp[1] = tmp[1].lower()
    if "x" in tmp[1]:
      s,e = tmp[1].split("x")
    else:
      s,e = tmp[1][1:].split("e")

    # Add to the list..
    episodes.append({'show_name':tmp[0], 'season_num':int(s), 'episode_num':int(e), 'episode_name':tmp[2], 'air_date':tmp[3]})
  return episodes



def create_score(line):
  """ Score the given line """
  line = line.lower()
  score = 0
  if "720p" in line: score += 100
  if "repack" in line: score += 10
  if "proper" in line: score += 10
  if "web-dl" in line: score += 20
  if "hdtv" in line: score += 10
  if "efnet" in line: score += 1 # efnet group posts are generally good
  return score



def filterResults(resList, maxAge, showdetails, HD):
  """ Get rid of stupid results """
  maxAge = float(maxAge) # make sure maxAge is a float.
  debug("FilterResults() called, maxAge=%s HD=%s" % (maxAge, HD))

  badnzbcounter = 0
  debug("*** Result List ***")
  for item in reversed(resList):
    # item = (full_post_name, id, size, group, age)
    itemName = item[0]
    itemID = item[1]
    itemSize = int(strtonum(item[2]))
    itemGroup = item[3]
    itemAge = float(strtonum(item[4]))

    debug("(%s) %s - %s - %s - %sd" % (itemID, itemName, itemSize, itemGroup, itemAge))

    # Check if NZB is in bad-nzbs list
    if hashlib.md5(itemID).hexdigest() in BAD_NZBS:
      debug("REMOVED - BAD NZB (%s)" % itemID)
      badnzbcounter += 1
      resList.remove(item)
      continue

    # Check for show name
    remove = True
    for n in getAltNames(showdetails['show_name']):
      t = [word for word in cleanup_name(n).split() if word.lower() in itemName.lower()]
      if len(t) == len(n.split()):
        # All words found so...
        remove = False
    if remove:
      debug("REMOVED - Required word not found in name ")
      resList.remove(item)
      continue

    # Check daily show date
    if showdetails['show_name'] in DAILY_SHOWS:
      # Check for Air-Date
      if showdetails['DAILYSHOWAIRDATE'].lower() not in itemName.lower():
        debug("REMOVED - NOT CORRECT DAILY-DATE")
        resList.remove(item)
        continue
    else:
      # Check for ep num
      se1 = "S%.2dE%.2d" % (showdetails['season_num'], showdetails['episode_num'])
      se2 = "%dX%.2d" % (showdetails['season_num'], showdetails['episode_num'])
      if se1.lower() not in itemName.lower() and se2.lower() not in itemName.lower():
        debug("REMOVED - NOT CORRECT EP NUM (%s)" % se1)
        resList.remove(item)
        continue

    # Remove if matches LOCAL_FILTERS
    if showdetails['show_name'] in LOCAL_FILTERS:
      req = LOCAL_FILTERS[showdetails['show_name']][0]
      filt = LOCAL_FILTERS[showdetails['show_name']][1]
      #Check req's..
      remove = False
      for r in req:
        if r.lower() not in itemName.lower():
          remove = True
          debug('REMOVED - LOCAL_FILTERS:REQ not matched')
          break
      #and filt's..
      for f in filt:
        if f.lower() in itemName.lower():
          remove = True
          debug('REMOVED - LOCAL_FILTERS:FILT matched')
          break
      if remove:
        resList.remove(item)
        continue

    # Remove if too big
    if itemSize > FILESIZE_LIMIT:
      debug("REMOVED - TOO BIG (%s)" % itemID)
      resList.remove(item)
      continue

    # Remove if wrong format
    if (HD and not "720p" in itemName.lower()): #TODO - check its SD properly?
      debug("REMOVED - DID NOT MATCH FORMAT HD='%s' (%s)" % (HD, itemID))
      resList.remove(item)
      continue

    # Remove if re does not match..
    if showdetails['show_name'] in REMATCH:
      if not re.findall(REMATCH[showdetails['show_name']], itemName):
        debug("REMOVED - DID NOT MATCH RE (%s)" % itemID)
        resList.remove(item)
        continue

    # Remove if name contains banned_words...
    tmp = ""
    for word in BANNED_WORDS:
      if word.lower() in item[0].lower():
        tmp = word.lower()
        break
    if tmp:
      debug("REMOVED - BANNED WORD '%s'" % tmp)
      resList.remove(item)
      continue


    # Remove if group is not in the allowed list..
    groups = [item[3]]
    if " " in item[3]:
      groups = item[3].split(" ")
    #debug("groups='%s'" % groups)
    groupcheck = True
    for group in groups:
      if group in BANNED_GROUPS:
        groupcheck = False
        break
    if not groupcheck:
      resList.remove(item)
      debug("REMOVED - BANNED GROUP '%s'" % item[3])
      continue


    # Remove if size does not meet minimum size
    if "720p" in item[0]:
      if item[2] < MINIMUM_POST_SIZE_720P:
        resList.remove(item)
        debug("REMOVED - BAD SIZE for 720p (%s < %s)" % (item[2], MINIMUM_POST_SIZE_720P))
        continue
    else:
      if item[2] < MINIMUM_POST_SIZE:
        resList.remove(item)
        debug("REMOVED - BAD SIZE for xvid (%s < %s)" % (item[2], MINIMUM_POST_SIZE))
        continue

    # Remove if post is older than air date
    if itemAge > maxAge:
      debug("REMOVED - OLDER THAN AIR DATE (%s > %s)" % (itemAge, maxAge))
      resList.remove(item)
      continue

    # Remove if older than users RETENTION_LIMIT
    if RETENTION_LIMIT > 0 and itemAge > RETENTION_LIMIT:
      debug("REMOVED - OVER RETENTION (%s > %s)" % (itemAge, RETENTION_LIMIT))
      resList.remove(item)
      continue

  if DEBUG:
    debug("*** Result List After Filtering ***")
    for item in resList:
      debug("  (%s) %s - %s - %s" % (item[1], item[0], item[2], item[3]))
    debug("*** End of Result List After Filtering ***")

  if badnzbcounter:
    printl(" Ignoring %s results as they have bad NZBs" % badnzbcounter)

  return resList



def cleanup_name(text):
  """ Clean unwanted characters from text and replace others """
  swaps = {':':'', '\'':'', '"':'', '(':'', ')':'', '!':'', '?':'', u'\u2019':'', '*':'',
           '/':' ', '\\':' ',
           '&':'and', u'\xe9':'e', u'\u03a3':'E', u'\xf6':'o', u'\xe4':'a'}
  for s in swaps:
    text = text.replace(s, swaps[s])
  return text



def strtonum(num):
  """Convert string to either int or float."""
  if type(num) in [int, float, long]:
    return num

  num = num.replace(',', '')

  try:
    ret = int(num)
  except ValueError:
    ret = float(num)
  return ret



def find_config():
  """ Find a config file and return the path """
  # Check users home dir for config file
  if os.access(os.path.join(os.path.expanduser("~"), "leechr.conf"), os.W_OK):
    return os.path.join(os.path.expanduser("~"), "leechr.conf")

  # Fall back to Default leechr directory
  return os.path.join(SCRIPTDIR, "leechr.conf")



class searchmodule(object):
  DOWNLOAD_URL = "%s"
  MULTISEARCH = True
  SLEEP_TIME_SEARCH = 7
  SLEEP_TIME_NZB = 7
  ERR_MSGS = []
  KILL_IF = [] # Remove from searcher list if string matches

  def expand_group_names(self, groupstring):
    """ Expand usenet group names.. a.b.c > alt.binaries.c """
    return groupstring.replace("a.b.", "alt.binaries.")

  def get_size(self, s):
    """ Convert string to size in MB """
    s = s.replace(",", "") # Remove commas
    s = s.replace("&nbsp;", " ") # Change &nbsp; to space

    tmp = re.findall(r"([\d.]*) ([K|M|G]?B)", s)
    if not tmp:
      return 0
    tmp = tmp[0] # get first result

    size = strtonum(tmp[0])
    if tmp[1] == "GB": return size * 1024.0
    elif tmp[1] == "KB": return round(size/1024.0, 2)
    elif tmp[1] == "B": return 0
    return size

  def get_age(self, when, format="%a, %d %b %Y %H:%M:%S"): # "Mon, 17 Nov 2008 01:45:32"
    """ Calculate age from date """
    debug("Called get_age('%s', '%s')" %(when, format))
    delta = datetime.now() - datetime.strptime(when, format)
    age = float("%.1f" % (delta.days + (delta.seconds/86400.0))) # divide secs into days
    return age

  def init_search(self, query, mode='RSS'):
    """ Download page and return data """

    # Before we begin do we need to Sleep some?
    if self.FRIENDLY_NAME in RETRIEVE_TIMES:
      t = RETRIEVE_TIMES[self.FRIENDLY_NAME] - int(time.time())
      if t > 0:
        printl(" Sleeping for %d secs..  Zzz.." % t)
        time.sleep(t)

    # Set new time
    RETRIEVE_TIMES[self.FRIENDLY_NAME] = int(time.time() + self.SLEEP_TIME_SEARCH)
    debug(RETRIEVE_TIMES)

    if self.NOT_CHAR:
      query = query.replace("%21", self.NOT_CHAR) # replace ! with specified not-char

    page = retrieve_url(self.RSS_BASE_URL % query, friendly_name=self.FRIENDLY_NAME)
    if not page and len(SEARCH_MODULES)>1:
      printl("[!] Error: %s appears to be down, we will skip it for this session." % self.FRIENDLY_NAME)
      SEARCH_MODULES_OFFLINE.append(self.__class__.__name__)
      return None

    p = "".join(page).lower()

    # Check KILL_IF errors
    for e in self.KILL_IF:
      if e.lower() in p:
        printl("[!] Error: %s had a problem, I have removed this module from active list. (%s)" % (self.FRIENDLY_NAME, e))
        SEARCH_MODULES_OFFLINE.append(self.__class__.__name__)
        return None

    # Check for errors in the page
    for error in self.ERR_MSGS:
      if error.lower() in p:
        printl("[!] Error: %s had a problem. (%s)" % (self.FRIENDLY_NAME, error))
        return None

    if mode.upper() == 'RSS':
      # Do the XML..
      xml = BeautifulStoneSoup(page)
      items = xml("item")
      if not items:
        debug("No items")
        return None
      else:
        return items
    elif mode.upper() == 'RAW':
      return page
    elif mode.upper() == 'HTML':
      return BeautifulSoup(page)
    elif mode.upper() == 'JSON':
      import json
      return json.loads(page)
    else:
      # Do HTML as standard
      return BeautifulSoup(page)





########################################################################
# B I N S E A R C H . I N F O
########################################################################
class BINSEARCHINFO(searchmodule):
  """
  BINSEARCHINFO module v1 by Ashy
  xx Apr 2013 - v1 Initial Release
  """
  FRIENDLY_NAME = "binsearch.info"
#  DOWNLOAD_URL = "%s"
  RSS_BASE_URL = "http://binsearch.info/index.php?q=%s&m=&max=100&adv_g=&adv_age=1100&adv_sort=date&adv_col=on&minsize=&maxsize=&font=&postdate="
  NOT_CHAR = ""

  def search(self, query, extra):
    """ Search and return the results """

    print query
    keys = query.split('+')
    print keys
    filters = [w[3:] for w in keys if w[:3] == '%21']
    keywords = [w for w in keys if w[3:] not in filters]
    print filters
    print keywords
    query = '+'.join(keywords)
    print query

    items = self.init_search(query, mode='HTML')
    if not items:
      return []

    rows = items.findAll('tr', {'onmouseover':'this.style.background=\'#D5D4F1\';'})

    resultList = []
    for i in rows:
      try:
        downloadName = i.contents[2].contents[0].contents[0]
        downloadID = i.contents[1].contents[0]['name']
        downloadGroup = i.contents[4].contents[0].contents[0]
        downloadAge = i.contents[5].contents[0]
        downloadSize = i.contents[2].contents[1]
      except:
        extype, exvalue = sys.exc_info()[:2]
        printl("[!] Error with module: %s (%s)" % (extype,exvalue))
        continue
      exit()

      # Create new item and check if we need to add it to the resultList..
      tmpItem = (downloadName, self.DOWNLOAD_URL % downloadID, downloadSize, downloadGroup, downloadAge)
      tmp = False
      for r in resultList:
        if tmpItem[1] in r:
          tmp = True
          break
      if tmp: # Already in the list so just continue
        continue

      resultList.append(tmpItem)
    return resultList



########################################################################
# N Z B S . O R G
########################################################################
class NZBSORG(searchmodule):
  """
  NZBSORG Module by DaSchug
  14 Oct 2010 - Initial release with minor-mods by Ashy
  12 May 2013 - Fixed to only .remove() categories if they exist
  """
  FRIENDLY_NAME = "nzbs.org"
  NOT_CHAR = "--"

  def __init__(self):
    self.DOWNLOAD_URL = "http://nzbs.org/api?t=get&id=%s&apikey=" + NZBSORG_APIKEY

  def search(self, query, extra):
    """ Search and return the results """
    tab = query.split('+')

    categories = []
    for word in tab:
      if word == "xvid":
        categories.append("5030")
        if 'xvid' in tab: tab.remove("xvid")
      elif word == "720p":
        categories.append("5040")
        if '720p' in tab: tab.remove("720p")
        if 'x264' in tab: tab.remove("x264")

    self.RSS_BASE_URL = "http://nzbs.org/api?t=search&q=%s" \
      + "&attrs=group" \
      + "&cat=" + ",".join(categories) \
      + "&apikey=" + NZBSORG_APIKEY

    filters = [word for word in tab if word[:3] == '%21' or word[0] == "-"]
    query2 = "+".join([word for word in tab if not word in filters])

    items = self.init_search(query2)
    if not items:
      return []

    debug("items: %s" % (len(items),))

    # Remove item that match a filter keyword
    def f(x):
      for f in filters:
        if f[3:] in decodeHTML(x.title.string):
          return False
      return True

    def tagToContens(tagList):
      contentList = []
      for tag in tagList:
        contentList.append(tag.string)
      return contentList

    #Make a nicer and duplicate free result list
    resultList = []
    for r in filter(f, items):
      downloadName = decodeHTML(r.title.string)
      description = decodeHTML(r.description.string)

      # Get downloadGroup
      res = r.findAll('newznab:attr', attrs={"name" : "group"})[0]['value']
      if not res:
        debug("Remove: %s (no group found)" % (downloadName,))
        continue
      downloadGroup = self.expand_group_names(res)

      # Get size
      res = r.findAll('newznab:attr', attrs={"name" : "size"})[0]['value']
      if not res:
        debug("Remove: %s (no size found)" % (downloadName,))
        continue
      downloadSize = strtonum(res) /1024 /1024

      # Get Id
      res = decodeHTML(r.guid.string)
      if not res:
        debug("Remove: %s (no id found)" % (downloadName,))
        continue
      downloadId = res

      # Get age
      res = decodeHTML(r.pubdate.string)
      if not res:
        debug("Remove: %s (no age found)" % (downloadName,))
        continue
      downloadAge = self.get_age(res[:-6], format="%a, %d %b %Y %H:%M:%S") # "Mon, 17 Nov 2008 01:45:32" #TODO use better date

      debug("name='%s' size='%d' group='%s' id='%s' age='%.2f'" % (downloadName, downloadSize, downloadGroup, downloadId, downloadAge))
      resultList.append((downloadName, self.DOWNLOAD_URL % downloadId, downloadSize, downloadGroup, downloadAge))


    return resultList



########################################################################
# N Z B C L U B . C O M
########################################################################
class NZBCLUBCOM(searchmodule):
  """
  NZBCLUBCOM module v3 by Ashy
  14 Jul 2015 - Rewritten to work with new site design (v2.6.11)
  05 Mar 2014 - Updated feed URL
  06 Dec 2010 - NZBClub decided to change their api so heres the new module - Ashy.
  03 Oct 2009 - Initial Release
  """
  FRIENDLY_NAME = "nzbclub.com"
  DOWNLOAD_URL = "http://www.nzbclub.com/nzb_get/{0}"
  RSS_BASE_URL = "http://www.nzbclub.com/search.aspx?q=%s" # "http://www.nzbclub.com/nzbfeeds.aspx?ss=%s"
  NOT_CHAR = "-"
  ERR_MSGS = ['Too Many Hit. Please slow down.']
  SLEEP_TIME_SEARCH = 7
  SLEEP_TIME_NZB = 20

  def search(self, query, extra):
    """ Search and return the results """
    html = self.init_search(query, mode='RAW')
    if not html:
      return []

    results = []
    items = re.findall(r"<div class=\"panel-body label-menu-corner bg-light.*?\">(.*?)votedown.*?</div>\r\n</div>", html, flags=re.DOTALL)
    for item in items:
      if '<a class="text-muted"' in item:
        continue # We don't want 'muted' items (they have been flagged as password etc)
      try:
        divs = re.findall(r"<div.*?>(.*?)</div>", item, flags=re.DOTALL)
        name = striphtmlentities(re.findall(r"<a class=\"text-primary\".*?>(.*?)</a>", divs[0], flags=re.DOTALL)[0])
        grp = re.findall(r"<a class=\"text-primary-2\".*?>(.*?)</a>", divs[0], flags=re.DOTALL)[0]
        size = self.get_size(re.findall(r"([\d,.]* [K|M|G]?B)", divs[1])[0])
        url = self.DOWNLOAD_URL.format(re.findall(r"collectionid=\"(.*?)\"", item)[0])
        age = str(re.findall(r"([\d.]* [d|h])", divs[2])[0])
        agenum = int(re.findall(r"([\d.]*)", age)[0])
        if "h" in age:
          age = 24/agenum
        elif "d" in age:
          age = agenum
      except:
        print "fail", sys.exc_info()[1]
        continue
      results.append((name, url, size, grp, age))
    return results



########################################################################
# newznab base class
########################################################################
class _newznab(searchmodule):
  """
  Newznab module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "newznab"
  RSS_BASE_URL = "newznab"
  NOT_CHAR = "!"
  ERR_MSGS = []
  MULTISEARCH = False

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query, mode='raw')
    if not items:
      return []

    root = ET.fromstring(items)

    channel = root.find('channel')
    if not channel:
      return []

    resultList = []
    for child in channel:
      if child.tag == 'item':
        dName = child.find('title').text
        dID = child.find('link').text
        dSize = strtonum(child.find('enclosure').get('length'))/1024/1024 # Make sure MB
        dGroup = u"leechr"
        dAge = self.get_age(child.find('pubDate').text[:-6]) # Chop timezone diff.
        resultList.append((dName, self.DOWNLOAD_URL % dID, dSize, dGroup, dAge))

    return list(set(resultList))



########################################################################
# N Z B N D X . C O M (newznab)
########################################################################
class NZBNDXCOM(_newznab):
  """
  NZBNDXCOM module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "nzbndx.com"
  KILL_IF = ['Request limit reached']

  def __init__(self):
    self.RSS_BASE_URL = "http://www.nzbndx.com/api?t=search&q=%s&apikey=" + NZBNDXCOM_APIKEY



########################################################################
# N Z B N D X . C O M (newznab)
########################################################################
class USENETCRAWLERCOM(_newznab):
  """
  USENETCRAWLERCOM module v1 by Ashy
  10 May 2013 - Initial Release
  """
  FRIENDLY_NAME = "usenet-crawler.com"

  def __init__(self):
    self.RSS_BASE_URL = "http://www.usenet-crawler.com/api?t=search&q=%s&apikey=" + USENETCRAWLERCOM_APIKEY



########################################################################
# L O C A L N E W Z N A B +
########################################################################
class LOCALNEWZNAB(_newznab):
  """
  LOCALNEWZNAB module v1 by Ashy
  15 May 2013 - Initial Release
  """
  FRIENDLY_NAME = "Local-Newznab+"

  def __init__(self):
    url = LOCALNEWZNAB_URL
    if url[:-1] != '/':
      url += '/' # add a slash
    self.RSS_BASE_URL = url + "api?t=search&q=%s&apikey=" + LOCALNEWZNAB_APIKEY



########################################################################
# N Z B . C C = DEAD
########################################################################
class _NZBCC(searchmodule):
  """
  NZBCC module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "nzb.cc"
  DOWNLOAD_URL = "http://nzb.cc/nzb.php?c=%s"
  RSS_BASE_URL = "http://nzb.cc/q.php?q=%s"
  NOT_CHAR = "-"
  ERR_MSGS = ["does not exist"]

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query, mode='RAW')
    if not items:
      return []

    items = re.findall(r'\[([0-9]+?),\"(.*?)\",\"(.*?)\",\"(.*?)\",\"(.*?)\",([0-9]+?),\"(.*?)\",\"(.*?)\"\]', items)
    if not items:
      return []

    resultList = []
    for i in items:
      dName = striphtmlentities(i[1])
      for t in ('<b>', '<\/b>'):
        dName = dName.replace(t, '')

      dID = i[0]
      dSize = i[5]
      dGroup = self.expand_group_names(i[4])
      dAge = i[6]

      if " days" in dAge:
        dAge = strtonum(dAge[:-5])
      elif " hours" in dAge:
        dAge = 0
      else:
        debug("FIXME: dAge is unknown!!!")
        dAge = 0

      resultList.append((dName, self.DOWNLOAD_URL % dID, dSize, dGroup, dAge))

    return list(set(resultList))



########################################################################
# N E W S H O S T . C O . Z A
########################################################################
class NEWSHOSTCOZA(searchmodule):
  """
  NEWSHOSTCOZA module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "newshost.co.za"
  DOWNLOAD_URL = "http://www.newshost.co.za/%s"
  RSS_BASE_URL = "http://www.newshost.co.za/?s=%s"
  NOT_CHAR = ""

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query, mode='HTML')
    if not items:
      return []

    resultList = []
    for i in items.findAll('tr')[5:]:
      tds = i.findAll('td')
      if len(tds) != 6:
        continue

      dAge = tds[4].text.lower()
      if 'h' in dAge:
        for r in [',', 'h']:
          dAge = dAge.replace(r, '')
        dAge = strtonum(dAge)/24.0
      elif 'm' in dAge:
        dAge = '0'
      else:
        for r in [',', 'd']:
          dAge = dAge.replace(r, '')

      dSize = striphtmlentities(tds[1].text)
      if "GB" in dSize:
        dSize = int(strtonum(dSize[:-3])*1024)
      elif "MB" in dSize:
        dSize = int(strtonum(dSize[:-3]))
      else:
        dSize = 1

      dCat = tds[2].text
      dID = tds[3].findAll('a')[0].get('href')
      dName = tds[5].text
      dGroup = u"leechr"
      resultList.append((dName, self.DOWNLOAD_URL % dID, dSize, dGroup, dAge))

    return list(set(resultList))



########################################################################
# S I C K B E A R D . C O M
########################################################################
class SICKBEARDCOM(searchmodule):
  """
  SICKBEARDCOM module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "sickbeard.com"
#  DOWNLOAD_URL = "%s"
  RSS_BASE_URL = "http://lolo.sickbeard.com/api?t=tvsearch&cat=5040,5030&q=%s"
  NOT_CHAR = ""
  MULTISEARCH = False

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query, mode='RSS')
    if not items:
      return []

    resultList = []
    for i in items:
      dName = decodeHTML(i.title.string)
      dAge = self.get_age(i.pubdate.string[:-6])
      dSize = int(strtonum(i.enclosure.get('length'))/1024/1024)
      dID = decodeHTML(i.link.string)
      dGroup = u"leechr"
      resultList.append((dName, self.DOWNLOAD_URL % dID, dSize, dGroup, dAge))

    return list(set(resultList))





########################################################################
# N Z B X . C O
########################################################################
class NZBXCO(searchmodule):
  """
  NZBXCO module v1 by Ashy
  19 Apr 2013 - Initial Release
  """
  FRIENDLY_NAME = "nzbx.co"
#  DOWNLOAD_URL = "%s"
  RSS_BASE_URL = "https://nzbx.co/api/search?q=%s"
  NOT_CHAR = "-"
  MULTISEARCH = False

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query, mode='JSON')
    if not items:
      return []

    resultList = []
    for i in items:
      dName = decodeHTML(i['name'])
      dAge = round((time.time()-i['postdate'])/60/60/24, 1)
      dSize = int(strtonum(i['size'])/1024/1024)
      dID = decodeHTML(i['nzb'])
      dGroup = u"leechr"
      resultList.append((dName, self.DOWNLOAD_URL % dID, dSize, dGroup, dAge))

    return list(set(resultList))





########################################################################
# N Z B I N D E X . N L
########################################################################
class NZBINDEXNL(searchmodule):
  """
  NZBIndex.nl Module
  """
  FRIENDLY_NAME = "nzbindex.nl"
#  DOWNLOAD_URL = "%s"
  RSS_BASE_URL = "http://www.nzbindex.nl/rss/?q=%s"
  NOT_CHAR = "-"

  def search(self, query, extra):
    """ Search and return the results """
    items = self.init_search(query)
    if not items:
      return []

    resultList = []
    for r in items:
      downloadName = decodeHTML(r.title.string)
      description = decodeHTML(r.description.string)
      try:
        downloadGroup = r.category.string
        downloadSize = self.get_size(re.findall(r"<b>([\d,.]* [K|M|G]?B)</b>", description)[0])
        downloadID = r.enclosure['url']
        downloadAge = self.get_age(r.pubdate.string[:-6]) # [:-6] to get rid of timezone
      except:
        printl("[!] Error with module: %s" % sys.exc_info()[0])
        continue

      resultList.append((downloadName, self.DOWNLOAD_URL % downloadID, downloadSize, downloadGroup, downloadAge))

    return list(set(resultList))



class Searcher(object):
  def __init__(self,moduleName):
    self.moduleName = moduleName
    self.searcher = eval(self.moduleName + "()")

  def search(self, query, extra):
    if not query:
      debug("no query")
    query = query.encode('utf-8') # fix more stupid unicode errors
    query = urllib.quote_plus(query) # convert spaces to plus and encode any wierd characters
    return self.searcher.search(query, extra)

#  def getDownloadURL(self):
#    return self.searcher.DOWNLOAD_URL






########################################################################
# M Y   E P I S O D E S
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
    try:
      page = urllib2.urlopen("http://www.myepisodes.com/shows.php?type=manage").read()
    except:
      printl("[!] Error opening URL to get show IDs")
      exit()

    # Find all shows and their IDs..
    shows = {}
    showids = re.findall("<option value=\"(\d*)\">(.*[^<])</option>", page.decode("utf-8"))
    if showids:
      #make a nice dictionary
      for show in showids:
        shows[show[1]] = show[0]
    else:
      printl("[!] Could not find any show IDs")
      exit()

    # Write them to the showid file
    try:
      f = open(os.path.join(SCRIPTDIR, "showids.dat"), "wb")
      pickle.dump(shows, f)
      f.close()
    except:
      printl("[!] Error: Could not save showids.dat for writing")
      exit()

    debug("Wrote showids.dat")
    return shows



  ####################################################################
  # L O A D   S H O W   I D S
  ####################################################################
  def loadShowIDs(self):
    """ Load the show-id list from file """
    try:
      f = open(os.path.join(SCRIPTDIR, "showids.dat"),"rb")
      data = pickle.load(f)
      f.close()
    except:
      return self.retrieveShowIDs()

    debug("Loaded showids.dat")
    return data


  ####################################################################
  # L O G I N
  ####################################################################
  def login(self):
    """ Login to myeps """
    url = "http://www.myepisodes.com/login.php"
    data = urllib.urlencode({"username":self.username, "password":self.password, "u":"views.php", "action":"Login"})
    req = urllib2.Request(url, data, {"User-Agent":USERAGENT})
    try:
      page = urllib2.urlopen(req).read()
    except KeyboardInterrupt:
      raise
    except:
      return False
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


  ####################################################################
  # G E T   S H O W   I D
  ####################################################################
  def getShowID(self, showName):
    """ Convert a show name to an ID """
    if not self.showlist:
      self.showlist = self.loadShowIDs()

    if showName in self.showlist:
      return self.showlist[showName]
    else:
      # We could not find the ShowID in our local list so retrieve a new list and try again
      self.showlist = self.retrieveShowIDs()
      if showName in self.showlist:
        return self.showlist[showName]

    # We couldn't find the show at all
    return False


  ####################################################################
  # S E T   A C Q U I R E D
  ####################################################################
  def setAcquired(self, showName, seasonNum, episodeNum):
    """ Set an episode as acquired """
    showID = self.getShowID(showName)
    if not showID:
      printl("[!] Error: Could not get ID for '%s'" % showName)
      return False

    # Lets try to 'acquire' the show :)..
    while True:
      try:
        page = urllib2.urlopen("http://www.myepisodes.com/myshows.php?action=Update&showid=%s&season=%s&episode=%s&seen=0" % (showID, seasonNum, episodeNum))
      except KeyboardInterrupt:
        raise
      except:
        printl("[!] Error opening URL to set show as acquired, will retry in %s secs" % RETRY_TIME)
        time.sleep(RETRY_TIME)
        printl("Retrying..")
        continue

      if self.getAcquired(showName, seasonNum, episodeNum, page):
        # TODO: make sure we did it
        break

    # We did it!!
    printl("Marked '%s S%02dE%02d' as acquired." % (showName,seasonNum,episodeNum)),
    return True


  ####################################################################
  # G E T   A C Q U I R E D
  ####################################################################
  def getAcquired(self, showName, seasonNum, episodeNum, page=None):
    """ Get an episode's acquired status """
    # TODO
    return True


  ####################################################################
  # G E T   S H O W   A I R   D A T E
  ####################################################################
  def getShowAirDate(self, showName, seasonNum, episodeNum):
    showID = self.getShowID(showName)
    if not showID:
      printl("[!] Error: Could not get ID for '%s'" % showName)
      return False

    seasonEpisode = "%02dx%02d" % (seasonNum, episodeNum)
    try:
      page = urllib2.urlopen("http://www.myepisodes.com/views.php?type=epsbyshow&showid=%s" % showID)
      soup = BeautifulSoup(page)
      thisEp = soup.find(text=seasonEpisode).parent.parent
      date = thisEp.find("td",{"class":"date"}).a.string
    except KeyboardInterrupt:
      raise
    except:
      printl("[!] Failed to find air-date for '%s %s'" % (showName, seasonEpisode))
      return False

    return date



def loadLeechrDatas():
  """ Load persistent datas """
  try:
    filename = os.path.join(SCRIPTDIR, "leechr.dat")
    f = open(filename, "rb")
    data = pickle.load(f)
    f.close()
    for i in _PERSISTENT:
      globals()[i] = data[i]
      debug("'%s' = '%s'" % (i, data[i]))
  except:
    debug("Couldn't load '%s'" % filename)
    return

  debug("Loaded persistent datas from '%s'" % filename)
  return

def saveLeechrDatas():
  """ Save persistent datas """
  try:
    filename = os.path.join(SCRIPTDIR, "leechr.dat")
    data = {}
    for i in _PERSISTENT:
      data[i] = globals()[i]
    f = open(filename, "wb")
    pickle.dump(data, f)
    f.close()
  except:
    debug("Couldn't save '%s' (%s)" % (filename, sys.exc_info()[:2]))
    return False

  debug("Wrote persistent datas to '%s'" % filename)
  return True


def stats_add(key, amount=1):
  """ Add to stats """
  if type(key) is not str:
    debug("key is not str")
    return
  if type(amount) not in [int, float, long]:
    debug("key is not number (%s)" % type(amount))
    return

  if key not in LEECHR_STATS:
    LEECHR_STATS[key] = 0
  LEECHR_STATS[key]+=amount


def getAltNames(name):
  """ Return alt-names if any """
  if name in ALT_SHOW_NAMES:
    return ALT_SHOW_NAMES[name]
  return [name]






if __name__ == '__main__':
  printl("Leechr v%s (C)2008-2013 Paul Ashton - http://ashysoft.wordpress.com" % LEECHR_VERSION)

  if sys.version_info[:3] < (2,5) or sys.version_info[:3] >= (3,0):
    printl("[!] Fatal Error: You need Python 2.5 or later (not 3.0+) to use this script.")
    exit()

  SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
  HELPERS_FILE = os.path.join(SCRIPTDIR, "helpers.dat")
  CONFIG_FILE = find_config()

  # Check command line args
  if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
      if arg == "/?" or arg == "--help":
        printl("\nUsage: python %s [OPTION]...\n" % __file__)
        printl("Options:")
        printl("   conf=FILENAME\t\tUse FILENAME as config file")
        printl("   debug\t\t\tTurn on DEBUG mode")
        exit()
      elif arg[:5].lower() == "conf=":
        CONFIG_FILE = os.path.abspath(arg[5:])
      elif arg[:5].lower() == "debug":
        DEBUG = True
        printl("DEBUG mode enabled.")
      elif arg[:4].lower() == "set=":
        printl("Setting '%s'" % arg[4:])
        exec(arg[4:])
      else:
        printl("[!] Warning: Unknown argument '%s'" % arg)


  printl("Config file = '%s'." % CONFIG_FILE)

  if not os.access(CONFIG_FILE, os.W_OK):
    printl("[!] Fatal Error: Could not open '%s'" % CONFIG_FILE)
    printl("[!] If you have not yet created it you can use 'example.conf' as a guide.")
    printl("[!] You may also specify your config file on the command line, for example \"python leechr.py conf=my.conf\"")
    exit()

  try:
      execfile(CONFIG_FILE)
  except:
      printl("[!] Fatal Error: Error loading '%s' (%s)" % (CONFIG_FILE, str(sys.exc_info())))
      exit()


  # Check .conf settings are usable
  if not ME_USERNAME or not ME_PASSWORD:
    printl("[!] Fatal Error: You need to set your MyEpisodes.com username and password in '%s'" % CONFIG_FILE)
    exit()
  if not NZBDir:
    printl("[!] Fatal Error: You need to set your NZBDir in '%s'" % CONFIG_FILE)
    exit()
  if not os.access(NZBDir, os.W_OK):
    printl("[!] Fatal Error: '%s' is not writable or does not exist." % NZBDir)
    exit()
  if not os.access(SCRIPTDIR, os.W_OK):
    printl("[!] Fatal Error: '%s' is not writable or does not exist." % SCRIPTDIR)
    exit()


  # Check for old settings
  if 'NZBS_APIKEY' in locals():
    printl("[!] Old-Setting Warning: NZBS_APIKEY is no longer used, please use NZBSORG_APIKEY instead!")
    time.sleep(2)


  # Make sure we have a log dir
  if not LOGDIR:
    LOGDIR = SCRIPTDIR


  # Check for API keys...
  if 'NZBSORG_APIKEY' not in locals() or not NZBSORG_APIKEY and 'NZBSORG' in SEARCH_MODULES:
    SEARCH_MODULES.remove('NZBSORG')
    printl('[!] Disabled \'NZBSORG\' module as NZBSORG_APIKEY is not set.')

  if 'NZBNDXCOM_APIKEY' not in locals() or not NZBNDXCOM_APIKEY and 'NZBNDXCOM' in SEARCH_MODULES:
    SEARCH_MODULES.remove('NZBNDXCOM')
    printl('[!] Disabled \'NZBNDXCOM\' module as NZBNDXCOM_APIKEY is not set.')

  if 'USENETCRAWLERCOM_APIKEY' not in locals() or not USENETCRAWLERCOM_APIKEY and 'USENETCRAWLERCOM' in SEARCH_MODULES:
    SEARCH_MODULES.remove('USENETCRAWLERCOM')
    printl('[!] Disabled \'USENETCRAWLERCOM\' module as USENETCRAWLERCOM_APIKEY is not set.')

  if 'LOCALNEWZNAB_APIKEY' not in locals() or not LOCALNEWZNAB_APIKEY and 'LOCALNEWZNAB' in SEARCH_MODULES:
    SEARCH_MODULES.remove('LOCALNEWZNAB')
    printl('[!] Disabled \'LOCALNEWZNAB\' module as LOCALNEWZNAB_APIKEY is not set.')

  if 'LOCALNEWZNAB_URL' not in locals() or not LOCALNEWZNAB_URL and 'LOCALNEWZNAB' in SEARCH_MODULES:
    SEARCH_MODULES.remove('LOCALNEWZNAB')
    printl('[!] Disabled \'LOCALNEWZNAB\' module as LOCALNEWZNAB_URL is not set.')



  # Check some settings..
  if USENET_USESSL and USENET_PORT == 119:
    printl("[!] Warning: USENET_USESSL is set but port is 119 (this should probably be 563)")
  if not USENET_USESSL and USENET_PORT == 563:
    printl("[!] Warning: USENET_USESSL is NOT set but port is 563 (this should probably be 119)")



  # Load helpers.dat..
  try:
    execfile(HELPERS_FILE)
    printl("Loaded helpers.dat v%s" % HELPERS_DAT_VERSION)
  except:
    printl("[!] Warning: Could not load helpers.dat (%s)" % str(sys.exc_info()))


  if LEECHR_REQ_VERSION > LEECHR_VERSION:
    printl("[!] \t#############################################################")
    printl("[!] \t# Due to some changes in the formatting of the helpers.dat file")
    printl("[!] \t# you are required to upgrade to Leechr v%s or later." % LEECHR_REQ_VERSION)
    printl("[!] \t# Please visit http://ashysoft.wordpress.com for downloads.")
    printl("[!] \t#############################################################")
    exit()

  # Load leechrs persistent data..
  loadLeechrDatas()

  stats_add('timesrun')

  # Set socket timeout
  socket.setdefaulttimeout(60) # max time 60 seconds

  if len(SEARCH_MODULES) < 1:
    printl("No active search modules")
    exit()

  sm = [locals()[sm].FRIENDLY_NAME for sm in SEARCH_MODULES] # Get some friendly names for modules
  printl("Active search modules: %s\n" % ", ".join(sm))

  # Login to myepisodes...
  printl("Logging in to myepisodes.com..")
  myeps = MyEpisodes(ME_USERNAME,ME_PASSWORD)
  if not myeps.login():
    printl("[!] Error logging in to myepisodes.com")
    exit()

  printl("Querying myepisodes.com..")
  toGrab = getEpisodeInfo()
  if not toGrab:
    exitmsg("Nothing to acquire, goodbye!")
    exit()

  # Sort toGrab shows into new,old
  # TODO: make this nicer its a mess :D
  old = []
  new = []
  oldText = []
  newText = []
  for i in toGrab:
    t = '%s S%.2dE%.2d' % (i['show_name'], i['season_num'], i['episode_num'])
    if i in DIDNT_FIND:
      old.append(i)
      oldText.append(t)
    else:
      new.append(i)
      newText.append(t)

  toGrab = new + old
  toGrabText = newText + oldText

  debug("old = %s" % old)
  debug("new = %s" % new)

  printl('\n%d shows to acquire (%d new): %s.' % (len(toGrab), len(new), ', '.join(toGrabText)))


  #We can reset DIDNT_FIND now :)
  DIDNT_FIND = []

  # Load timeout data
  EPISODE_TIMEOUTS = load_timeouts()

  ########################################################################
  # Search for the eps
  ########################################################################
  startTime = time.time()
  downloadCount = 0
  setAcquireFail = 0
  for showNum in range(len(toGrab)):
    i = toGrab[showNum] # {'show_name':, 'season_num':, 'episode_num':, 'episode_name':, 'air_date':}
    debug(i)

    nse = "%s S%.2dE%.2d" % (i['show_name'], i['season_num'], i['episode_num'])
    maxAge = float(getMyEpsAge(i['air_date'])) + float(DAYS_EARLY)
    se = ""

    # Work out time remaining...
    timeTaken = round(time.time()-startTime)
    if showNum>0:
      t = (timeTaken/showNum) * (len(toGrab)-showNum)
      if t > 60:
        timeLeft = " [%dm]" % round(t/60)
      else:
        timeLeft = " [%ds]" % t
    else:
      timeLeft = ""

    progress = "[%s/%s]%s" % (showNum+1, len(toGrab), timeLeft)

    # Skip any shows in the ignore list
    if i['show_name'] in IGNORE_SHOWS:
      printl("%s Skipping '%s' as it is in your ignore list." % (progress, nse))
      continue

    # Check if episode is too old..
    age = getMyEpsAge(i['air_date'])
    if IGNORE_EPISODES_OLDER_THAN:
      if float(age) > float(IGNORE_EPISODES_OLDER_THAN):
        printl("%s Skipping '%s' as it is older than %d days. (%s days)" % (progress, nse, IGNORE_EPISODES_OLDER_THAN, age))
        continue

    # Should this ep be in HD?
    if GET_HD_VIDEO:
      HD = True
      if i['show_name'] in SD_OVERRIDE:
        HD = False
    else:
      HD = False
      if i['show_name'] in HD_OVERRIDE:
        HD = True

    # Check if show is listed as an SD show in helpers..
    if i['show_name'] in SD_SHOWS:
      HD = False

    printl("")
    debug("Ep age = %s" % age)

    # Check timeouts
    found = False
    for t in range(len(EPISODE_TIMEOUTS)):
      if EPISODE_TIMEOUTS[t][0] == i['show_name'] and EPISODE_TIMEOUTS[t][1] == i['season_num'] and EPISODE_TIMEOUTS[t][2] == i['episode_num']:
        found = True
        break
    switched = ""
    if found:
      if TIMEOUT_ATTEMPTS > 0:
        switched = " - Will switch in %s attemps" % (TIMEOUT_ATTEMPTS-EPISODE_TIMEOUTS[t][3])
        if EPISODE_TIMEOUTS[t][3] >= TIMEOUT_ATTEMPTS:
          if HD:
            HD = False
            switched = " - Switched from HD after %s attempts" % TIMEOUT_ATTEMPTS
          else:
            HD = True
            switched = " - Switched from SD after %s attempts" % TIMEOUT_ATTEMPTS
      elif TIMEOUT_DAYS > 0:
        switched = " - Will switch in %s days" % (float(TIMEOUT_DAYS)-age)
        if age >= float(TIMEOUT_DAYS):
          if HD:
            HD = False # Switch to alternate format
            switched = " - Switched from HD after %s days" % float(TIMEOUT_DAYS)
          else:
            HD = True # Switch to alternate format
            switched = " - Switched from SD after %s days" % float(TIMEOUT_DAYS)

    # Make query string and tell user whats happening..
    if HD:
      query_format = " 720p"
      printl("%s Searching for '%s' (HD%s):" % (progress, nse, switched))
    else:
      query_format = " !720p !1080p"
      printl("%s Searching for '%s' (SD%s):" % (progress, nse, switched))

    helpers = ""
    shifted = ""
    daily = ""
    named = ""

    # Add search helpers..
    if i['show_name'] in SEARCH_HELPERS:
      helpers = " %s" % SEARCH_HELPERS[i['show_name']]

    #Shift show season/ep if needed..
    if i['show_name'] in SEASON_EP_SHIFT:
      shiftInfo = SEASON_EP_SHIFT[i['show_name']] # [(season start, ep start, season end, ep end, season shift, ep shift)...]
      for shift in shiftInfo:
        debug("shift = '%s'" % str(shift))
        if (i['season_num'] >= shift[0] and i['episode_num'] >= shift[1] and
            i['season_num'] <= shift[2] and i['episode_num'] <= shift[3]):
          shifted = (i['season_num'], i['episode_num'])
          i['season_num'] += shift[4]
          i['episode_num'] += shift[5]
          printl(" Shifted from 'S%.2dE%.2d' to 'S%.2dE%.2d'." % (shifted[0], shifted[1], i['season_num'], i['episode_num']))
          break


    # DAILY_SHOWS - Swap ep number for date..
    if i['show_name'] in DAILY_SHOWS:
      printl("Retrieving air-date from myepisodes.com..")
      airDate = myeps.getShowAirDate(i['show_name'], i['season_num'], i['episode_num'])
      if not airDate: airDate = i['air_date']
      daily = datetime.strptime(airDate, "%d-%b-%Y").strftime("%Y.%m.%d")
      i['DAILYSHOWAIRDATE'] = daily
      printl("Using air-date '%s' for daily show.." % daily)
      debug("Daily-show '%s' > '%s'" % (i['air_date'], se))

    # NAMED_SHOWS - Swap ep number for ep-name..
    if i['show_name'] in NAMED_SHOWS:
      named = i['episode_name']
      printl("Using ep-name '%s' for named show.." % named)
      debug("Named-show 'S%.2dE%.2d' > '%s'" % (i['season_num'], i['episode_num'], se))



    ##############################################################################################################
    #  if shifted:
    #    i['season_num'], i['episode_num'] = shifted

    #Check timeouts
    found = False
    for t in range(len(EPISODE_TIMEOUTS)):
      if EPISODE_TIMEOUTS[t][0] == i['show_name'] and EPISODE_TIMEOUTS[t][1] == i['season_num'] and EPISODE_TIMEOUTS[t][2] == i['episode_num']:
        found = True
        break

    if found:
      # Increase attempts
      EPISODE_TIMEOUTS[t][3] += 1
      debug("Timeouts - Increased attempts")
    else:
      # Add episode to the timeout list
      EPISODE_TIMEOUTS.append([i['show_name'], i['season_num'], i['episode_num'], 1]) #[show_name, season_num, episode_num, attempts]
      debug("Timeouts - Added episode")

    debug("timeouts: %s" % str(EPISODE_TIMEOUTS))
    save_timeouts(EPISODE_TIMEOUTS)
    ##############################################################################################################

    tmpFilename = ""

    for module in SEARCH_MODULES:
      debug(module)
      # Do we need to skip this module?
      if module in SEARCH_MODULES_OFFLINE:
        debug('^ skipping this one')
        continue

      # Activate module..
      printl('\nChecking %s..' % (globals()[module].FRIENDLY_NAME))
      try:
        searcher = Searcher(module)
      except:
        printl('[!] Error with module (%s, %s)' % sys.exc_info()[:2])
        continue

      # Do we need to change the show name?
      name_list = getAltNames(i['show_name'])
      debug("Name_list: %s" % name_list)

      # Clear master result list..
      masterResultList = []

      tmpFilename = ""

      for n in name_list:
        # Create episode format list
        if daily:
          epis = [daily]
        elif named:
          epis = [named]
        else:
          epis = []
          if searcher.searcher.MULTISEARCH:
            for fmt in EPISODE_FORMATS:
              epis.append(fmt % (i['season_num'], i['episode_num']))
          else:
            # Only search for one episode format (we don't want to use too many API calls)
            epis.append(EPISODE_FORMATS[0] % (i['season_num'], i['episode_num']))
        debug("epis='%s'" % epis)

        for epi in epis:
          # Make our search query..
          query = cleanup_name(n) + " " + cleanup_name(epi) + helpers + query_format

          # ask searcher for some results..
          try:
            res = searcher.search(query, i) # pass i as extra info if needed
          except KeyboardInterrupt:
            raise
          except:
            printl("[!] Error: Module exception: %s" % str(sys.exc_info()[:2]))
            continue

          stats_add('searches')

          debug("searcher results='%s'" % res)
          resultList = filterResults(res, maxAge, i, HD)

          if resultList:
            masterResultList += resultList
            break # Break the 'epis' loop as we have results :)

      masterResultList = list(set(masterResultList)) # Get rid of dupes
      if not masterResultList:
        printl(" No results.")
        continue #continue to next module


      # Score up the results..
      scores = []
      for item in masterResultList:
        s = create_score(item[0])
        scores.append([s,item])

      # Sort results, highest score first..
      scores = sorted(scores, key=lambda i: i[0], reverse=True)


      # Display results..
      printl("%s matches:" % len(masterResultList))
      for s in range(len(scores)):
        printl(" (%s) %s %s" % (s+1, scores[s][0], scores[s][1][0]), wrap=False)


      # Try the results..
      for counter in range(len(scores)):
        printl("Grabbing NZB (%s).." % (counter+1))
        grabThis = scores[counter][1]


        # Before we being do we need to Sleep some?
        if searcher.searcher.FRIENDLY_NAME+"_NZB" in RETRIEVE_TIMES:
          t = RETRIEVE_TIMES[searcher.searcher.FRIENDLY_NAME+"_NZB"] - int(time.time())
          if t > 0:
            printl("Sleeping for %d secs..  Zzz.." % t)
            time.sleep(t)

        # Set new time
        RETRIEVE_TIMES[searcher.searcher.FRIENDLY_NAME+"_NZB"] = int(time.time() + searcher.searcher.SLEEP_TIME_NZB)
        debug(RETRIEVE_TIMES)


        # Grab NZB
        nzbdata = retrieve_url(grabThis[1])
        stats_add('nzbgets')
        if not nzbdata:
          printl("[!] Error: Could not retrieve NZB.")
          continue

        if not USENET_HOST:
          printl("[!] Warning: Usenet account has not been set up, can't check NZB contents. NZB may contain undesirable files.")
        else:
          printl("Checking NZB contents..")

          #Check for site errors in nzbdata
          error = False
          for e in searcher.searcher.ERR_MSGS:
            debug(e)
            if e.lower() in nzbdata.lower():
              error = e
              break
          if error:
            printl("[!] Error: %s had a problem. (%s)" % (searcher.searcher.FRIENDLY_NAME, error))
            continue

          #Make sure its an xml file
          if not "<?xml" in nzbdata.lower():
            printl("[!] Warning: Invalid NZB file, probably a site error.")
            stats_add('nzbfails')
            continue

          # Check it for passworded rars..
          c = check_for_passwords(nzbdata)
          if c:
            BAD_NZBS[hashlib.md5(grabThis[1]).hexdigest()] = c
            printl("[!] Warning: I Will ignore this NZB in the future (%s)" % c)
            debug("Added '%s' to BAD_NZBS for '%s'" % (grabThis[1], c))
            stats_add('nzbfails')
            continue

          printl("NZB appears OK, proceeding..")

        if not DONT_STRIP_NZBS:
          nzbdata = process_nzb(nzbdata, NZB_UNWANTED_FILES)
          if not nzbdata:
            stats_add('nzbfails')
            continue

        if USE_SCENE_NAMES:
          sre = re.compile(r".*EFNet\]-\[ (.*) \]-");
          if sre.findall(scores[counter][1][0]):
            sre2 = sre.findall(scores[counter][1][0])
            nse = sre2[0]

        nzbName = "%s%s%s.nzb" % (NZBprefix, nse, NZBsuffix)
        nzbName = cleanup_name(nzbName)

        # Download NZB
        if NZB_SUBDIRS:
          subdir = cleanup_name(i['show_name'])
          tmpFilename = os.path.join(NZBDir, subdir)

          if not os.access(tmpFilename, os.F_OK): # Doesn't exist already
            debug("Dir '%s' doesn't exist, creating it.." % tmpFilename)
            os.makedirs(tmpFilename)

          tmpFilename = os.path.join(NZBDir, subdir, nzbName)
        else:
          tmpFilename = os.path.join(NZBDir, nzbName)

        break

      if not tmpFilename:
        printl("[!] Error: No valid NZB file")
        continue #move to next searcher

      break #we must have a working result so break from search_modules loop


    #end of SEARCH_MODULES for loop


    if not tmpFilename:
      printl("\n No results from any search module, sorry!")
      if shifted:
        i['season_num'], i['episode_num'] = shifted # Shift back
      DIDNT_FIND.append(i)
      continue #to next show



    # We should have a usable NZB by here

    # Save NZB
    f = write_file(nzbdata, tmpFilename)
    if f:
      printl("Saved NZB to '%s'." % f)
      downloadCount += 1

      # Tell myeps that we have acquired it..
      if AUTOMARK_ACQUIRE:
        if shifted:
          i['season_num'], i['episode_num'] = shifted # Make sure we mark correct ep if its shifted :)
        if not myeps.setAcquired(i['show_name'], i['season_num'], i['episode_num']):
          printl("[!] Warning: Failed to set acquired on myeps")
          setAcquireFail += 1
    else:
      printl("[!] Error: Something went wrong. FAILED to write NZB file :( Please report this!")





  printl("")
  if downloadCount and setAcquireFail:
    printl("[!] #########################################################")
    printl("[!] \tNOTE: For some reason, one or more of your episodes were not marked")
    printl("[!] \tas 'acquired' on MyEpisodes.com. Please do this manually.")
    printl("[!] #########################################################")

  # We're all done here, so bai!
  totalTime = round(time.time()-startTime)
  stats_add('timerunning',int(totalTime))

  tt = "%dm%.2ds" % (totalTime/60, totalTime%60)
  if downloadCount:
    if len(toGrab) != downloadCount:
      exitmsg("Grabbed %s of %s NZBs in %s, happy viewing!" % (downloadCount, len(toGrab), tt))
    else:
      exitmsg("Grabbed all %s NZBs in %s, happy viewing!" % (downloadCount, tt))
  else:
    exitmsg("All done, sorry it took me %s to find nothing :'(" % tt)
  saveLeechrDatas()

  debug(LEECHR_STATS)

