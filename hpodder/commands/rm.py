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


"""This is the remove podcast(s) command for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other hpodder modules
from hpodder.lib.db import get_selected_podcasts, remove_podcast
from hpodder.lib.utils import exe_name, mutex


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-24"
__license__   = "GPL"
__version__   = "0.1"


def _i( msg):
    logging.info( "rm: " + str( msg))

def _w( msg):
    logging.warning( "rm: " + str( msg))

_usage_text = "Usage: %prog rm <castid>..."
_helptext = _usage_text + """

Remove the specified podcast(s) entirely from the %prog database."""

def _rm_worker( args, gcp, gdbh):
    "Remove podcasts and associated episodes from database"
    parser = OptionParser( usage=_helptext)
    (options, args) = parser.parse_args( args=args)
    if len( args) < 1:
        _w( "rm requires a podcast ID to remove; " + \
            "please see {0} rm --help".format( exe_name()))
        return
    pcl = get_selected_podcasts( gdbh, args)
    if len( pcl) < 1:
        _w( """No podcasts were found with the specified castid(s).
You can find your podcast IDs with "{0} lscasts".""".format( exe_name()))
        return
    _i( "Will remove the following podcasts:")
    _cmd_dict[ "lscasts"]( args=args, gcp=gcp, gdbh=gdbh)
    resp = raw_input( """
Are you SURE you want to remove these {0} podcast(s)?
Type YES exactly as shown, in all caps, to delete them.
Remove podcasts? """.format( len( pcl)))
    if resp == "YES":
        for pc in pcl:
            remove_podcast( gdbh, pc)
        gdbh.commit()
        _i( "Remove completed.")
    else:
        _i( "Remove aborted by user.")


def _cmd_worker( args, gcp, gdbh):
    "Hold database mutex while running the rm command"
    with mutex():
        _rm_worker( args, gcp, gdbh)

_cmd_dict = None

def register_self( reg_callback):
    global _cmd_dict
    _cmd_dict = \
        reg_callback( name="rm", descrip="Remove podcast(s) from the database",
                      func=_cmd_worker, usage_text=_usage_text)
