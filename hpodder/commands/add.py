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


"""This is the add podcast(s) command for hpodder ported to python.
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
from hpodder.lib.db import add_podcast
from hpodder.lib.ppod_types import PCEnabled, Podcast

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-23"
__license__   = "GPL"
__version__   = "0.1"


def _w( msg):
    logging.warning( "add: " + str( msg))


_usage_text = "Usage: %prog add <feedurl>..."

def _cmd_worker( args, gcp, gdbh):
    "Add new podcasts"
    parser = OptionParser( usage=_usage_text)
    (options, args) = parser.parse_args( args=args)
    if len( args) < 1:
        _w( "Feed URL required; Adding none has no effect.")
        return
    print( "Podcast(s) added:")
    fmt_str = "{0:4}  {1}"
    print( fmt_str.format( " ID", " URL"))
    print( fmt_str.format( "----",
           "-------------------------------------------------------"))
    for u in args:
        url = str( u)
        pc = add_podcast( gdbh, Podcast( castid=0, castname="", feedurl=url,
                                        pcenabled=PCEnabled.Enabled,
                                        failedattempts=0) )
        gdbh.commit()
        print( fmt_str.format( pc.castid, url, pc))


def register_self( reg_callback):
    reg_callback( name="add", func=_cmd_worker, usage_text=_usage_text)

