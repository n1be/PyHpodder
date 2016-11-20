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


"""This is the fetch podcast(s) command for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function, unicode_literals
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# Other hpodder modules
from hpodder.lib.config import get_option
from hpodder.lib.utils import generic_id_help


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-02-15"
__license__   = "GPL"
__version__   = "0.1"


_usage_text = "Usage: %prog fetch [<castid>...]"
_helptext = _usage_text + """

The fetch command will cause %prog to scan all feeds (as with
"%prog update") and then download all new episodes (as with
"%prog download").  Fetch is the default %prog command; fetch
will be executed if %prog is run with no arguments.

""" + generic_id_help( "podcast")


def _fetch_worker( args, gcp, gdbh):
    "Scan feeds, then download new episodes"
    parser = OptionParser( usage=_helptext)
    (options, args) = parser.parse_args( args=args)

    # Instead of doing a fetch, show the introduction if never seen already...
    showintro = get_option( gcp, "general", "showintro").lower()
    if showintro.count( "no") + showintro.count( "false"):
        _cmd_dict[ "update"]( args=args, gcp=gcp, gdbh=gdbh)
        _cmd_dict[ "download"]( args=args, gcp=gcp, gdbh=gdbh)
    else:
        _cmd_dict[ "setup"]( args=args, gcp=gcp, gdbh=gdbh)


_cmd_dict = None

def register_self( reg_callback):
    global _cmd_dict
    _cmd_dict = \
        reg_callback( name="fetch",
                      func=_fetch_worker, usage_text=_usage_text)
