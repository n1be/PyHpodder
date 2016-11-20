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


"""This is the catchup command for hpodder ported to python.
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
from hpodder.lib.db import get_all_pc_episodes, get_selected_podcasts, \
                           update_episode
from hpodder.lib.ppod_types import EpisodeStatus
from hpodder.lib.utils import generic_id_help, mutex


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-24"
__license__   = "GPL"
__version__   = "0.1"


def _i( msg):
    logging.info( "catchup: " + str( msg))

def _d( msg):
    "Print debugging messages"
    logging.debug( "catchup: " + str( msg))


_usage_text = "Usage: %prog catchup [-n NUM] [<castid>...]"
_helptext = _usage_text + """

Running catchup will cause %prog to mark all but the NUM most recent
episodes as Skipped.  This will prevent %prog from automatically
downloading such episodes.  You can specify the value for NUM with -n.

""" + generic_id_help( "podcast")


def _catchup_podcast( gdbh, n, pc):
    "catchup one podcast"
    _i( " * Podcast {0.castid}: {0.castname}".format( pc))
    eps = get_all_pc_episodes( gdbh, pc)
    if n > 0:
        eps_to_process = eps[:-n]
    else:
        eps_to_process = eps
    for ep in eps_to_process:
        if ep.epstatus == EpisodeStatus.Pending or \
           ep.epstatus == EpisodeStatus.Error:
            _d( (pc.castid, ep.epid, str(ep.epstatus) + " -> Skipped"))
            ep.epstatus = EpisodeStatus.Skipped
            update_episode( gdbh, ep)
        else:
            _d( (pc.castid, ep.epid, str(ep.epstatus)))
    gdbh.commit()


def _catchup_worker( args, gcp, gdbh):
    "Ignore older episodes of selected podcasts"
    parser = OptionParser( usage=_helptext)
    parser.set_defaults( n=1)
    parser.add_option( "-n", type="int", metavar="NUM",
                       help="Number of episodes not to be skipped (default 1)")
    (options, args) = parser.parse_args( args=args)
    podcasts = get_selected_podcasts( gdbh, args)
    _i( "{0} podcast(s) to consider:".format( len( podcasts)))
    for pc in podcasts:
        _catchup_podcast( gdbh, options.n, pc)


def _cmd_worker( args, gcp, gdbh):
    "Hold database mutex while running the catchup command"
    with mutex():
        _catchup_worker( args, gcp, gdbh)


def register_self( reg_callback):
    reg_callback( name="catchup", descrip="Ignore older undownloaded episodes",
                  func=_cmd_worker, usage_text=_usage_text)
