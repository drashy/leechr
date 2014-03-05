Leechr (c)2008-2013 Paul Ashton
http://ashysoft.wordpress.com

========================================================================
 W E L C O M E
========================================================================

Leechr will attempt to grab the .NZB for any episodes you have
on myepisodes.com that are not marked as 'acquired'.


If you have any comments, suggestions or bug reports please get in
touch via:
  web: http://ashysoft.wordpress.com
  email: drashy at gmail dot com
  or file an issue on the Leechr google code page @ http://code.google.com/p/leechr/

I hope you find this software useful and if you do, please consider
buying me a beer :)
http://ashysoft.wordpress.com/donate

~Ashy



========================================================================
 B E F O R E   Y O U   S T A R T
========================================================================

Requirements:
 - You will need Python 2.6 or later (NOT 3.0) installed. You can get it from http://python.org/download/

 - You will need an account on http://www.myepisodes.com

 - To take advantage of automatic nature of Leechr your news-reader should be able to automatically
   import NZB files from a directory of your choice.
   HellaNZB (http://www.hellanzb.com) and NewsLeecher (http://www.newsleecher.com) are two good
   choices but other news-readers *are* available.

 - You will also need lots of disk space and a nice fat net connection ;)



========================================================================
 H O W   T O   G E T   U P   A N D   R U N N I N G
========================================================================

Step 1
  *** If you already have a myepisodes.com account, skip to Step 2. ***

  If you have not already signed up to myepisodes.com, do that now.
  Now login and add any shows that you would like.


Step 2
  Copy example.conf to leechr.conf or just rename it.
  Open up leechr.conf in your favorite editor.

  There are three things you NEED to setup, see example.conf for
  explanations:

    ME_USERNAME = ""
    ME_PASSWORD = ""
    NZBDir = ""

  And a few more that are beneficial, set these up so Leechr can use
  your usenet account to check the contents of files before you
  download them.

    USENET_USESSL = False
    USENET_HOST = ""
    USENET_PORT = 119
    USENET_USERNAME = ""
    USENET_PASSWORD = ""

  Once you have set these up, save and close the file.


Step 3
  You now have two options:

  Option 1:
    (Very time consuming if you watch a lot of shows)
    Go through your shows on myepisodes.com and make sure that any
    episodes that you have already acquired are marked as such or
    Leechr will try to grab the .NZB for them.

  Option 2:
    Use the 'mark_all_acquired.py' script to set them *ALL* as acquired.
    Now goto myepisodes.com and uncheck all the shows that you want.


Step 4
  Run leechr.py and enjoy!




========================================================================
 T H A N K S
========================================================================

Many thanks go to the following for without them this project
would not exit:

  MyEpisodes (http://www.myepisodes.com)
  NewzLeech (http://www.newzleech.com)
  BeautifulSoup (http://www.crummy.com/software/BeautifulSoup/)

Also thanks to Sammy, Sharpy and Trin and all the other beta testers.
If you would like to become a beta tester just email me, I can always
use more testers :)


