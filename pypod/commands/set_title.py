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

"""This file implements the set podcast title command."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other pypod modules
from pypod.lib.db import get_selected_podcasts, update_podcast
from pypod.lib.utils import exe_name

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-24"
__license__   = "GPLv3"
__version__   = "0.2"


def _w( msg):
    logging.warning( "settitle: " + str( msg))


_usage_text = 'Usage: %prog settitle -c <castid> -t "TITLE"'
_help_text = _usage_text + """

You must specify one podcast ID with -c and the new title with -t.
If the title contains spaces, you must enclose it in quotes."""

_generic_help = " see " + exe_name() + " settitle --help"


def _cmd_worker( args, gcp, gdbh):
    "Modify the stored title of a podcast"
    parser = OptionParser( usage=_help_text)
    parser.add_option( "-c", "--castid", type="int", metavar="ID",
                       help="Podcast ID to modify")
    parser.add_option( "-t", "--title", type="string", metavar="TITLE",
                       help="New title for this podcast")
    (options, args) = parser.parse_args( args=args)
    if options.castid == None:
        _w( "--castid required;" + _generic_help)
        return
    if options.title == None:
        _w( "--title required;" + _generic_help)
        return
    if len( args) > 0:
        _w( "Excess arguments: " + str(args) + ";" + _generic_help)
        return
    pcl = get_selected_podcasts( gdbh, [ options.castid])
    if len( pcl) < 1:
        _w( "Invalid podcast ID given")
    else:
        pc = pcl[0]
        pc.castname = options.title
        update_podcast( gdbh, pc)
        gdbh.commit()


def register_self( reg_callback):
    reg_callback( name="settitle", func=_cmd_worker, usage_text=_usage_text)

