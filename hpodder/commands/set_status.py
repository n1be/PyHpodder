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


"""This is the set episode status command for hpodder ported to python.
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
from hpodder.lib.db import get_selected_podcasts, get_selected_pc_episodes, \
                           update_episode
from hpodder.lib.ppod_types import EpisodeStatus, string_to_enum
from hpodder.lib.utils import exe_name, mutex

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-29"
__license__   = "GPL"
__version__   = "0.1"


def _d( msg):
    logging.debug( "setstatus: " + str( msg))

def _w( msg):
    logging.warning( "setstatus: " + str( msg))


_usage_text = \
    "Usage: %prog setstatus -c <castid> -s <status> <episodeid>..."
_help_text = _usage_text + """

You must specify one podcast ID with -c, one new status with -s.
You must also specify one or more episode ID.  To select all episodes,
specify episodeid "all"."""

_generic_help = " see " + exe_name() + " setstatus --help"


def _get_all_status_names():
    names = ""
    for s in EpisodeStatus:
        if names:
            names += ", "
        names += str( s)
    return names


_status_help_text = \
    "Specify the new status.  Possible statuses are: " + _get_all_status_names()

def _cmd_worker( args, gcp, gdbh):
    "Modify the status of selected episodes"
    parser = OptionParser( usage=_help_text)
    parser.add_option( "-c", "--castid", type="int", metavar="ID",
                       help="Podcast ID in which the episodes occur")
    parser.add_option( "-s", "--status", type="string", metavar="STATUS",
                       help=_status_help_text)
    (options, args) = parser.parse_args( args=args)
    if options.castid == None:
        _w( "--castid required;" + _generic_help)
        return
    if options.status == None:
        _w( "--status required;" + _generic_help)
        return
    try:
        new_status = string_to_enum( options.status, EpisodeStatus)
    except AttributeError:
        _w( "Invalid status supplied; use one of: " + _get_all_status_names())
        return
    if len( args) < 1:
        _w( "episode IDs missing;" + _generic_help)
        return
    with mutex():
        _setstatus_worker( gdbh, options.castid, new_status, args)

def _setstatus_worker( gdbh, castid, new_status, args):
        podcastlist = get_selected_podcasts( gdbh, [ castid])
        if len( podcastlist) < 1:
            _w( "--castid did not give a valid podcast id")
        else:
            eplist = get_selected_pc_episodes( gdbh, podcastlist[0], args)
            _d( "Modifying {0} episodes".format( len( eplist)))
            if len( eplist):
                for ep in eplist:
                    ep.epstatus = new_status
                    ep.epfailedattempts = 0
                    update_episode( gdbh, ep)
                gdbh.commit()
            else:
                _w( "No episodes found for modification.")


def register_self( reg_callback):
    reg_callback( name="setstatus", func=_cmd_worker, usage_text=_usage_text)
