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

"""This file implements the commands to enable and disable update/download of selected podcasts."""

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
from pypod.lib.datatypes import PCEnabled
from pypod.lib.utils import exe_name, mutex


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-24"
__license__   = "GPLv3"
__version__   = "0.2"


def _d( msg):
    "Print debugging messages"
    logging.debug( "enable/disable: " + str( msg))

def _w( msg):
    logging.warning( str( msg))


_disable_usage_text = "Usage: %prog disable <castid>..."
_disable_helptext = _disable_usage_text + """

Disables selected podcasts -- they will no longer be downloaded or
updated until re-enabled."""

_enable_usage_text = "Usage: %prog enable <castid>..."
_enable_helptext = _enable_usage_text + """

Enables selected podcasts for downloading and updating"""


def _both_worker( args, gcp, gdbh, newstat):
    "Enable and Disable downloading given podcasts"
    podcast_list = get_selected_podcasts( gdbh, args)
    _d( "Setting {0} podcasts to {1}".format( len(podcast_list), newstat))
    for pc in podcast_list:
        pc.pcenabled = newstat
        if pc.is_enabled:
            pc.failedattempts = 0
        update_podcast( gdbh, pc)
    gdbh.commit()


def _cmd_worker( args, gcp, gdbh, cmd, newstat):
    "Hold database mutex while running the enable or disable command"
    if len( args) < 1:
        _w( cmd + " requires a podcast ID; "
           "please see " + exe_name() + " " + cmd + " --help")
    else:
        with mutex():
            _both_worker( args, gcp, gdbh, newstat)


def _disable_worker( args, gcp, gdbh):
    "Stop updating and downloading given podcasts"
    parser = OptionParser( usage=_disable_helptext)
    (options, args) = parser.parse_args( args=args)
    _cmd_worker( args, gcp, gdbh, "disable", PCEnabled.UserDisabled)

def _enable_worker( args, gcp, gdbh):
    "Enable podcasts that were previously disabled"
    parser = OptionParser( usage=_enable_helptext)
    (options, args) = parser.parse_args( args=args)
    _cmd_worker( args, gcp, gdbh, "enable", PCEnabled.Enabled)


def register_self( reg_callback):
    reg_callback( name="enable", func=_enable_worker,
                  usage_text=_enable_usage_text)
    reg_callback( name="disable", func=_disable_worker,
                  usage_text=_disable_usage_text)
