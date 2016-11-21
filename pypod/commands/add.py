#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Robert N. Evans

#
# PyPod - A podcast media aggregator.  This program is a re-implementation
# of John Goerzen's no longer supported hpodder utility.
#
# PyPod is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# PyPod is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""This file implements the add command for subscribing to new podcasts."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other pypod modules
from pypod.lib.db import add_podcast
from pypod.lib.datatypes import PCEnabled, Podcast

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-21"
__license__   = "GPLv3"
__version__   = "0.2"


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
        pc = Podcast( feedurl=url)
        add_podcast( gdbh, pc)
        gdbh.commit()
        print( fmt_str.format( pc.castid, url, pc))


def register_self( reg_callback):
    reg_callback( name="add", func=_cmd_worker, usage_text=_usage_text)

