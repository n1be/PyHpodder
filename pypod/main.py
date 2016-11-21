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

"""This file defines the callable main probram of pypod."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
import os
import sys
try:
    str = unicode
except NameError:
    pass

# other pypod modules
from commands import implemented_commands
from lib.config import load_config
from lib.db import connect, disconnect
from lib.utils import exe_name, init_dirs


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-21"
__license__   = "GPLv3"
__version__   = "0.2"

_debug = 0

def main( argv=None):
    "Callable main program for pypod"
    try:
        prog = os.path.basename( argv[0])
    except( TypeError, IndexError):
        raise ValueError(
                  exe_name() + " must be called with non-empty argument list")

    usage_help = """Usage: %(prog)s [global-options] <command> [command-options]
 Run "%(prog)s lscommands" for a list of available commands.
 Run "%(prog)s <command> -h" for help on a particular command.
 Run "%(prog)s -h" for available global-options.""" % locals()

    parser = OptionParser( usage=usage_help, add_help_option=False)
    parser.add_option( "-?", "-h", "--help", action="help",
                       help="Show this help message and exit.")
    parser.add_option( "-d", "--debug", dest="debug", action="store_true",
                       default=False, help="Enable debugging printouts.")
    parser.disable_interspersed_args() # Stop parsing at cmd verb
    (optargs, command_args) = parser.parse_args()
    if _debug:
        print( "optargs: {0!s}".format( optargs))
        print( "Command tail: {0!s}".format( command_args))
    if optargs.debug:
        logging.basicConfig( level=logging.DEBUG,
                             format="%(levelname)s %(message)s")
    else:
        logging.basicConfig( level=logging.INFO,
                             format="%(levelname)s %(message)s")

    if len( command_args) == 0:
        command_name = "fetch"    # 'fetch all' is the default command
    else:
        command_name = command_args.pop(0)
    try:
        cmd = implemented_commands[ command_name]
    except KeyError:
        raise ValueError(
            "Unsupported command: {0}\n{1}".format( command_name, usage_help))

    init_dirs()
    cp=load_config()
    dbh=connect()
    cmd( args=command_args, gcp=cp, gdbh=dbh)
    disconnect( dbh)


if __name__ == "__main__":
    main()
