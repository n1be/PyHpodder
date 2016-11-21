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

"""This file implements the commands to list podcasts / episodes."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other pypod modules
from pypod.lib.db import get_all_pc_episodes, get_selected_podcasts
from pypod.lib.utils import generic_id_help

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-24"
__license__   = "GPLv3"
__version__   = "0.2"


# --------------------------------------------------
#   lscasts

_lscasts_usage = "Usage: %prog lscasts [-l] [<castid>...]"
_lscasts_help = _lscasts_usage + """

""" + generic_id_help( "podcast")

def _lscasts_worker( args, gcp, gdbh):
    "List subscribed podcasts"
    parser = OptionParser( usage=_lscasts_help)
    parser.add_option( "-l", dest="islong", action="store_true", default=False,
                       help="Long format display -- include URLs in output")
    (options, args) = parser.parse_args( args=args)
    pc_fmt = "{0:<4} {1:>4}/{2:<4} {3}"
    print( pc_fmt.format( " ID", "Pend", "Tot", "Title"))
    if options.islong:
        url_fmt = "               {0}"
        print( url_fmt.format( "URL"))
    print( pc_fmt.format( "----", "----", "----",
                          "----------------------------------------"))
    for pc in get_selected_podcasts( gdbh, args):
        pend = gdbh.execute("""SELECT COUNT(*) FROM episodes
                                 WHERE castid = ? AND status = 'Pending'""",
                            ( pc.castid, )).fetchone()[0]
        tot = gdbh.execute("""SELECT COUNT(*) FROM episodes
                                WHERE castid = ?""",
                           ( pc.castid, )).fetchone()[0]
        print( pc_fmt.format( pc.castid, pend, tot,
                              pc.disabled_str + pc.castname))
        if options.islong:
            print( url_fmt.format( pc.feedurl))


# --------------------------------------------------
#   lsepisodes

_lsepisodes_usage = "Usage: %prog lsepisodes [-l] [<castid>...]"
_lsepisodes_help = _lsepisodes_usage + """

""" + generic_id_help( "podcast") + """
You can find your podcast IDs with "%prog lscasts"."""

def _lsepisodes_worker( args, gcp, gdbh):
    "List episodes in the database"
    parser = OptionParser( usage=_lsepisodes_help)
    parser.add_option( "-l", dest="islong", action="store_true", default=False,
                       help="Long format display -- include URLs in output")
    (options, args) = parser.parse_args( args=args)
    ep_fmt = "{0:<4} {1:<4} {2:<4.4} {3:<65.65}"
    print( ep_fmt.format( "PcId", "EpId", "Stts", "Episode Title"))
    if options.islong:
        url_fmt = "               {0}"
        print( url_fmt.format( "Episode URL"))
    print( ep_fmt.format( "----", "----", "----",
         "----------------------------------------------------------------------"))
    for pc in get_selected_podcasts( gdbh, args):
        for ep in get_all_pc_episodes( gdbh, pc):
            print( ep_fmt.format( ep.podcast.castid, ep.epid, ep.epstatus,
                                  ep.eptitle))
            if options.islong:
                print( url_fmt.format( ep.epurl))


# --------------------------------------------------
#   command registration

def register_self( reg_callback):
    reg_callback( name="lscasts",
                  func=_lscasts_worker, usage_text=_lscasts_usage)
    reg_callback( name="lsepisodes",
                  func=_lsepisodes_worker, usage_text=_lsepisodes_usage)
    ## Not used
    # reg_callback( name="lseps", descrip="Alias for lsepisodes",
    #               func=_lsepisodes_worker, usage_text=_lsepisodes_usage)
