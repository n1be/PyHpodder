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

"""This file implements the command dispatcher for pypod.  When new commands are added, this file needs to be modified to call the implementation of the command(s)."""

# standard library imports
from __future__ import print_function, unicode_literals
from optparse import OptionParser
import string
from types import FunctionType, UnicodeType
try:
    str = unicode
except NameError:
    pass

from pypod.lib.utils import exe_name
# pypod command modules
import add
import catchup
import download
import enable_disable
import fetch
import ls
import rm
import set_status
import set_title
import setup
import update


# List public names
__all__ = [ 'implemented_commands']

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-21"
__license__   = "GPLv3"
__version__   = "0.2"


def _check_type( t, val, name, none_allowed=None):
    "common type checking"
    if none_allowed and val == None:
        return
    t2 = type( val)
    if t2 != t:
        raise TypeError( "{0} ({1}) must be {2}".format( name, t2, t))

class _ImplementedCommand( object):
    """Class to wrap command implementation with description and usage strings"""

    def __init__( self, func, descrip, usage_text=None):
        _check_type( FunctionType, func, 'func')
        self.__func = func
        _check_type( UnicodeType, descrip, 'descrip')
        if not descrip:
            raise ValueError( "'descrip' must be non-zero length")
        self.__descrip = descrip
        _check_type( UnicodeType, usage_text, 'usage_text', none_allowed=True)
        self.__usage_text = usage_text

    def __call__( self, args, gcp, gdbh):
        return self.__func( args, gcp, gdbh)

    @property
    def descrip( self):
        """Get the command description"""
        return self.__descrip

    @property
    def usage_text( self):
        """Get the usage text for the command"""
        return self.__usage_text


class _TruncatedKeyDict( dict):
    "Dictionary that allows lookup by unique truncated keys"

    def __contains__( self, key):
        return super( _TruncatedKeyDict, self).__contains__( key) or \
            len( [x for x in self.keys() if x.startswith( key)]) == 1

    def __missing__( self, key):
        num_found = 0;
        for x in self.keys():
            if x.startswith( key):
                num_found += 1
                real_key = x
        if num_found == 1:
            return self[ real_key]
        raise KeyError( key)


# global commands dictionary
implemented_commands = _TruncatedKeyDict( {})

def _register_command( name, func, descrip=None, usage_text=None):
    _check_type( UnicodeType, name, 'name')
    if name == "":
        raise ValueError( "Command name may not be empty string")
    if name in implemented_commands:
        raise ValueError( 'Command "{0}" is already registered'.format( name))
    implemented_commands[ name] = _ImplementedCommand( func,
                                                       descrip or func.__doc__,
                                                       usage_text)
    # for commands that use other commands...
    return implemented_commands


_lscommands_usage = """Usage: %prog lscommands [-l]"""

def _lscommands_worker( args, gcp, gdbh):
    """Display a list of all available commands"""
    parser = OptionParser( usage=_lscommands_usage)
    parser.add_option( "-l", dest="islong", action="store_true", default=False,
                       help="Long format -- display usage of each command")
    (options, args) = parser.parse_args( args=args)
    print( "All available commands:")
    fmt_str = "{0:10}  {1}"
    print( fmt_str.format( " Name", " Description"))
    print( fmt_str.format( "----------",
           "-------------------------------------------------------------"))
    names = implemented_commands.keys()
    names.sort()
    print
    for name in names:
        cmd = implemented_commands[name]
        if cmd.descrip != "hidden":
            print( fmt_str.format( name, cmd.descrip))
            if options.islong and cmd.usage_text:
                ut = string.join(
                    string.split( cmd.usage_text, '%prog '),
                    exe_name() + ' ')
                print( fmt_str.format( "", ut))
                print( " -" * 36)


# Register my command
_register_command( 'lscommands', _lscommands_worker,
                   usage_text="Usage: %prog lscommands [-l]")


# Register other commands
add.register_self( _register_command)
catchup.register_self( _register_command)
download.register_self( _register_command)
enable_disable.register_self( _register_command)
fetch.register_self( _register_command)
ls.register_self( _register_command)
rm.register_self( _register_command)
set_status.register_self( _register_command)
set_title.register_self( _register_command)
setup.register_self( _register_command)
update.register_self( _register_command)
