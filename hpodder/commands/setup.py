#!/usr/bin/env python

#
# PyHpodder - A podcast media aggregator
# Copyright (C) 2010, Robert N. Evans
#
# PyHpodder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# PyHpodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


"""This is the setup command for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder

This command is not available to the user by default -- it is
run on first execution of fetch"""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other hpodder modules
from hpodder.lib.config import get_config_path, get_option, load_config
from hpodder.lib.utils import exe_name, mutex


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-24"
__license__   = "GPL"
__version__   = "0.1"


def _d( msg):
    "Print debugging messages"
    logging.debug( "setup: " + str( msg))


_sample_urls = [
    "http://soundofhistory.complete.org/files_soh/podcast.xml",
    "http://www.thelinuxlink.net/tllts/tllts.rss",
    "http://www.itconversations.com/rss/recentWithEnclosures.php",
    "http://www.sciam.com/podcast/sciam_podcast_r.xml",
    "http://www.npr.org/rss/podcast.php?id=510019",
    "http://amateurtraveler.com/podcast/rss.xml",
    "http://broadband.wgbh.org/amex/rss/podcast_np.xml",
    "http://www.npr.org/rss/podcast.php?id=700000" ]


def _subscribe_to_samples( args, gcp, gdbh):
    print( "OK, just a moment while I initialize those feeds for you...")
    _cmd_dict[ "add"]( _sample_urls, gcp, gdbh)
    ## NYI...
    ## _cmd_dict[ "update"]( [], gcp, gdbh)
    _cmd_dict[ "catchup"]( [ "-n", "1"], gcp, gdbh)
    ## By intent, download is not called.
    ## _cmd_dict[ "download"]( [], gcp, gdbh)



def _setup_worker( args, gcp, gdbh):
    cp = load_config()
    defaultloc = get_option( cp, "DEFAULT", "downloaddir")
    _d( "DEFAULT downloaddir = {0}".format( defaultloc))
    print( """Hello!  Welcome to {0}!

It looks like this is your first time running {0}, so we're going
to take care of a few very quick matters.

First, where would you like to store your downloaded podcast episodes?
You can just press Enter to accept the default location in the brackets,
or enter your own location (full path, please!)
""".format( exe_name()))

    dlloc_inp = raw_input( "  Download Location [" + defaultloc + "]: ")
    print( """

OK!  Last question:  Would you like {0} to
automatically subscribe you to a few sample podcasts?  This could be a nice
way to see what's out there.  You can always remove these or add your own
later.
""".format( exe_name()))

    subscribe_inp = raw_input( "  Subscribe to sample podcasts? [Y/n] ")
    cpfile = open( get_config_path(), 'w')
    if dlloc_inp.strip() != "":
        dldircfg = "[DEFAULT]\n\ndownloaddir = {0}\n".format( dlloc_inp)
    else:
        dldircfg = ""
    cpfile.write( dldircfg + """
[general]

; The following line tells {0} that
; you have already gone through the intro.
showintro = no
""".format( exe_name()))

    cpfile.close()
    if subscribe_inp in [ '', 'y', 'Y']:
        _subscribe_to_samples( args, load_config(), gdbh)
    else:
        print( """OK, as you wish, I won't add the sample subscriptions.
You can find the list of samples later in the {0} manual.
""".format( exe_name()))

    print( """
OK, {0} is ready to run!  Each time you want to
download new episodes, just run {0}.  If you let me subscribe you
to episodes, type {0} and hit Enter to start the podcasts downloading!

Don't forget to check the {0} manual for more tips on {0}!

""".format( exe_name()))


def _cmd_worker( args, gcp, gdbh):
    "Hold database mutex while running the setup command"
    with mutex():
        _setup_worker( args, gcp, gdbh)


_cmd_dict = None

def register_self( reg_callback):
    global _cmd_dict
    _cmd_dict = \
        reg_callback( name="setup", descrip="hidden", func=_cmd_worker)
