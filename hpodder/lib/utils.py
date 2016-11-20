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


"""This is the miscellaneous utility routines for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function, unicode_literals
from contextlib import contextmanager
import fcntl
import logging
import os
import string
import sys
try:
    str = unicode
except NameError:
    pass

# other hpodder modules
from config import get_app_dir, get_encl_tmp


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-03"
__license__   = "GPL"
__version__   = "0.1"


def _d( msg):
    "Print debugging messages"
    logging.debug( "utils: " + str( msg))


def generic_id_help( name=None):
    "Return a common help string describing ID usage"
    fmt_str = \
"""You can optionally specify one or more {0}{1}IDs.  If
given, only those IDs will be selected for processing.
The special id "all" will select all {0}{1}IDs.
If no ID is given, then "all" will be used."""
    if name:
        spacer = " "
    else:
        spacer = " "
    return fmt_str.format( name, spacer)


def exe_name():
    "Return the basename of the executable file now running"
    return os.path.basename( sys.argv[0])


@contextmanager
def mutex():
    """Execute func while holding a (file lock) mutex.
This method prevents other processes from acquiring the mutex while it is held,
but it does not prevent multiple concurrent attempts from the same process.
It has the advantage that aborting the process releases the lock."""
    lockfd = os.open( os.path.join( get_app_dir(), '.lock'),
                      os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
    try:
        fcntl.lockf( lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _d( "Acquired MUTEX")
    except:
        _d( "Failed to acquire MUTEX")
        os.close( lockfd)
        print( "Aborting because another command is already running")
        raise
    yield
    _d( "Releasing MUTEX")
    fcntl.lockf( lockfd, fcntl.LOCK_UN)
    os.close( lockfd)


def sanitize_basic( inp):
    """Remove control characters from input string"""
    r = filter( lambda c: c not in '\n\r\t\000', inp)
    # Strip leading hyphen
    if r.startswith( '-'):
        return r[1:]
    return r


def sanitize_filename( inp):
    """Replace bad filename characters by an underscore"""
    OK_chars = string.digits + string.letters + '#$+,-.=@_'
    r = ''.join( map( lambda c: c not in OK_chars and '_' or c,
                      sanitize_basic( inp)))
    while '__' in r:
	r = r.replace( '__', '_')
    r = r.strip( "_-")
    if r != '':
        return r
    return "UNKNOWN"


def init_dirs():
    """Create application working and non-volatile storage directories"""
    for d in [ get_app_dir(), get_encl_tmp() ]:
        if not os.path.isdir( d):
            os.makedirs( d)


def empty_dir( path):
    "Delete files in a given directory, but not the directory itself"
    for root, dirs, files in os.walk( path, topdown=False):
        for name in files:
            os.remove( os.path.join( root, name))
        for name in dirs:
            os.rmdir( os.path.join( root, name))


if __name__ == '__main__':
    # Test code
    print( __doc__)
    print( )
    print( "Testing sanitize_basic")
    print( "sanitize_basic( '-begin_' + '\\n\\r\\t\\000' + '_end') =")
    s =     sanitize_basic( '-begin_' + '\n\r\t\000' + '_end')
    print( "{0} (length = {1})".format( s, len( s)))
    print( )
    print( "Testing sanitize_filename of chars 0:65535")
    s = ''.join( map( unichr, range(65536)))
    s = sanitize_filename( s)
    print( "{0} (length = {1})".format( s, len( s)))
    print( )
    print( "ContextManager 'mutex'")
    with mutex():
        print( "Holding one copy of the mutex, will attempt to get another")
        with mutex():
            print( "Got second mutex")
