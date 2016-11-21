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

"""This file defines the classes for Podcast (feed) and Episode (attachment)
application-specific datatypes."""

# standard library imports
from __future__ import print_function, unicode_literals
import sys
try:
    str = unicode
except NameError:
    pass

# PyPI module enum, not in standard library until Python 3.4.
try:
    import enum
except ImportError:
    print( """
  Error: Module "enum" not found. Please install "python-enum".  If this
         package is not available for your OS, the enum package can be
         downloaded from the Python Package Index,
         http://pypi.python.org/pypi/enum
""", file=sys.stderr)
    sys.exit(1)

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-10"
__license__   = "GPLv3"
__version__   = "0.2"


# Enum of episode status values
EpisodeStatus = enum.Enum( 'Pending',	# Ready to download
                        'Downloaded',	# Already downloaded
                        'Error',	# Error downloading
                        'Skipped')	# Skipped by some process

# Enum of whether podcast is enabled
PCEnabled = enum.Enum( 'UserDisabled', 'Enabled', 'ErrorDisabled')

def string_to_enum( str, type):
    "Convert a string to an enumerated value"
    if str not in type:
        raise AttributeError( "{0!s} object has no attribute '{1!s}'"
                              .format( type, str))
    exec "choice = type.{0}".format( str)
    return choice


class _AppDict( dict):
    """Dictionary-like superclass for application datatypes:
    Members cannot be added or deleted after initialization.
    The data type of member value is not allowed to change."""

    def __init__( self, **members):
        super( _AppDict, self).__init__( members)

    def __repr__( self):
        str = ""
        for key in sorted( self.keys()):
            str = "{0}, {1!s}:{2!r}".format( str, key, self[key])
        return "{0!s}({1})".format(self.__class__, str[1:])

    def __getattribute__( self, name):
        "Allow reading member value as an attribute"
        try:
            return self[ name]
        except KeyError:
            # Read an actual attribute
            return super( _AppDict, self).__getattribute__( name)

    def __setattr__( self, name, value):
        "Allow setting member value as an attribute"
        try:
            self[ name] = value;
        except KeyError:
            # Create or Modify actual attribute
            super( _AppDict, self).__setattr__( name, value)

    def __setitem__( self, key, value):
        "Apply constraints upon setting member values"
        if key not in self:
            raise KeyError( "'{0!s}' has no member '{1!s}'"
                            .format( self.__class__, key))
        if self[ key] != None or \
           value == None:
            oldtype = type( self[ key])
        else:
            oldtype = int # None can become an int
        newtype = type( value)
        if newtype == oldtype:
            super( _AppDict, self).__setitem__( key, value)
        else:
            raise TypeError( "{0!s}[({1!s})'{2!s}'] cannot store '{3!s}'"
                             .format( self.__class__, oldtype, key, newtype))

    def __delitem__( self, key):
        raise TypeError( "Can not delete members from {0!s}"
                         .format( self.__class__))


class Podcast( _AppDict):
    """Data about feeds that have been subscribed
    { castid ::         Integer,
      castname ::       String,
      feedurl ::        String,
      pcenabled ::      PCEnabled,
      lastupdate ::     Maybe Integer, -- Last successful update
      lastattempt ::    Maybe Integer, -- Last attempt
      failedattempts :: Integer}       -- failed attempts since last success
"""

    def __init__( self, feedurl, castid=0, castname='', pcenabled=PCEnabled.Enabled,
                  failedattempts=0, lastupdate=None, lastattempt=None):

        # First initialize dict to establish keys and datatypes
        super( Podcast, self).__init__( castid=0, castname='', feedurl='',
                                        pcenabled=PCEnabled[0], lastupdate=None,
                                        lastattempt=None, failedattempts=0)
        for mbr in ( 'castid', 'castname', 'feedurl', 'pcenabled',
                     'failedattempts', 'lastupdate', 'lastattempt'):
            exec ( "self[ '{0}'] = {0}".format( mbr))

    @property
    def is_enabled( self):
        return self.pcenabled == PCEnabled.Enabled

    @property
    def disabled_str( self):
        if self.is_enabled:
            return ''
        elif self.pcenabled == PCEnabled.ErrorDisabled:
            return "[disabled by errors] "
        else:
            return "[disabled] "

    def __str__( self):
        return "Podcast {0} {1}{2}".format( self.castid, self.disabled_str,
                                             self.castname)


class Episode( _AppDict):
    """Data about one enclosure/attachment
    {podcast ::          Podcast,
     epid ::             Integer,
     eptitle ::          String,
     epurl ::            String,
     epguid ::           Maybe String,
     eptype ::           String,
     epstatus ::         EpisodeStatus,
     eplength ::         Integer,
     epfirstattempt ::   Maybe Integer, -- Last successful update
     eplastattempt ::    Maybe Integer, -- Last attempt
     epfailedattempts :: Integer}
"""

    def __init__( self, podcast, epid, eptitle, epurl, epguid, eptype,
                  epstatus, eplength, epfirstattempt=None, eplastattempt=None,
                  epfailedattempts=0):
        if type( podcast) != Podcast:
            raise TypeError( "'podcast'=:{0}: is not member of class Podcast" \
                             .format( podcast))
            
        # Initialize dict to establish datatypes
        super( Episode, self).__init__( podcast=podcast, epid=0, eptitle='',
            epurl='', epguid='', eptype='', epstatus=EpisodeStatus[ 0],
            eplength=0, epfirstattempt=None, eplastattempt=None,
            epfailedattempts=0)

        for mbr in ( 'podcast', 'epid', 'eptitle', 'epurl', 'epguid', 'eptype',
                     'epstatus', 'eplength', 'epfirstattempt', 'eplastattempt',
                     'epfailedattempts'):
            exec ( "self[ '{0}'] = {0}".format( mbr))

    def __str__( self):
        return "{0.podcast.castid:5d} {0.epid:5d} {0.epstatus!s:4.4} {0.eptitle}" \
                .format( self)

## --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -- 

def test():
    "Test code to run when invoked on the command line"
    print( __doc__)
    print()
    print( 'EpisodeStatus: ' + EpisodeStatus.__doc__)
    print( 'len( EpisodeStatus) =', len( EpisodeStatus))
    print( 'for i in EpisodeStatus:')
    print( '  print repr(i)')
    for i in EpisodeStatus:
        print( ". {0!r}".format( i))
    print( 'EpisodeStatus[0] =',  EpisodeStatus[0])
    print( 'EpisodeStatus[1] =',  EpisodeStatus[1])
    print( 'EpisodeStatus[2] =',  EpisodeStatus[2])
    print( 'EpisodeStatus[3] =',  EpisodeStatus[3])
    print( 'EpisodeStatus[-4] =',  EpisodeStatus[-4])
    print( 'EpisodeStatus[-3] =',  EpisodeStatus[-3])
    print( 'EpisodeStatus[-2] =',  EpisodeStatus[-2])
    print( 'EpisodeStatus[-1] =',  EpisodeStatus[-1])
    print( 'EpisodeStatus.Pending =',  EpisodeStatus.Pending)
    print( 'EpisodeStatus.Downloaded =',  EpisodeStatus.Downloaded)
    print( 'EpisodeStatus.Error =',  EpisodeStatus.Error)
    print( 'EpisodeStatus.Skipped =',  EpisodeStatus.Skipped)
    print( 'EpisodeStatus.Skipped.index =',  EpisodeStatus.Skipped.index)
    print( 'EpisodeStatus[0] == EpisodeStatus.Pending =',
            EpisodeStatus[0] == EpisodeStatus.Pending)
    print( 'EpisodeStatus[1] == EpisodeStatus.Pending =',
            EpisodeStatus[1] == EpisodeStatus.Pending)
    print( 'EpisodeStatus[1] != EpisodeStatus.Pending =',
            EpisodeStatus[1] != EpisodeStatus.Pending)
    print( 'EpisodeStatus[1] != EpisodeStatus.Downloaded =',
            EpisodeStatus[1] != EpisodeStatus.Downloaded)
    print( 'EpisodeStatus[0].__str__() =',  EpisodeStatus[0].__str__())
    print( 'EpisodeStatus[0].__repr__() =',  EpisodeStatus[0].__repr__())
    print( '"Pending" in EpisodeStatus =',  "Pending" in EpisodeStatus)
    print( '"Foo" in EpisodeStatus =',  "Foo" in EpisodeStatus)

    print("\n")
    print( 'repr( string_to_enum( "Pending", EpisodeStatus)) =',
            repr( string_to_enum( "Pending", EpisodeStatus)))
    try:
        print( 'INVALID: repr( string_to_enum( "Baz", EpisodeStatus)) ...')
        repr( string_to_enum( "Baz", EpisodeStatus))
        raise AssertionError( "Unknown enum value Baz was not detected")
    except AttributeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    try:
        print( "INVALID: EpisodeStatus[4] ...")
        EpisodeStatus[4]
        raise AssertionError( "Invalid enum index was not detected")
    except IndexError as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: EpisodeStatus.Foo ...")
        EpisodeStatus.Foo
        raise AssertionError( "Invalid attribute reference was not detected")
    except AttributeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( 'PCEnabled: ' + PCEnabled.__doc__)
    print( 'for i in PCEnabled:')
    print( '  print i.index, str(i)')
    for i in PCEnabled:
        print( ". {0.index!s} {0!s}".format( i))

    print("\n")
    print( "p1 = Podcast('URL1', 1, 'name1', PCEnabled.ErrorDisabled, 7)")
    p1 = Podcast('URL1', 1, 'name1', PCEnabled.ErrorDisabled, 7)

    print("\n")
    print( "p1.__doc__: {0}".format( p1.__doc__))

    print("\n")
    print( "str(p1): {0!s}".format(p1))

    print("\n")
    print( "repr(p1): {0!r}".format(p1))

    print("\n")
    print( "p1.castid: {0}".format( p1.castid))


    print("\n")
    try:
        print( "INVALID: p1.foo ...")
        p1.foo
        raise AssertionError( "Invalid attribute reference was not detected")
    except AttributeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( "CREATE A NEW ATTRIBUTE: p1.foo = 9 ...")
    p1.foo = 9
    print( "p1.foo: {0}".format( p1.foo))

    print("\n")
    print( "p1.castid = 6")
    p1.castid = 6
    print( "p1.castid: {0}".format( p1.castid))

    print("\n")
    try:
        print( "INVALID: p1.castid = '9' ...")
        p1.castid = '9'
        raise AssertionError( "Invalid attribute datatype assignment was not detected")
    except TypeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( "p1.lastupdate = 99")
    p1.lastupdate = 99
    print( "p1.lastupdate: {0}".format( p1.lastupdate))

    print("\n")
    try:
        print( "INVALID: delattr(p1, 'foobar')  ...")
        delattr(p1, 'foobar')
        raise AssertionError( "Invalid attribute deletion was not detected")
    except AttributeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    try:
        print( "INVALID: del p1.lastupdate  ...")
        del p1.lastupdate
        raise AssertionError( "Attribute deletion was not detected")
    except AttributeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( "p1['feedurl'] = 'different_URL'")
    p1['feedurl'] = 'different_URL'
    print( "p1['feedurl']: {0}".format( p1['feedurl']))

    print("\n")
    try:
        print( "INVALID: p1['baz']  ...")
        p1['baz']
        raise AssertionError( "Unknown key reference was not detected")
    except KeyError as e:
        print( ". {0!r}".format( e))

    print("\n")
    try:
        print( "INVALID: p1['baz'] = 'foo' ...")
        p1['baz'] = 'foo'
        raise AssertionError( "Unknown key assignment was not detected")
    except KeyError as e:
        print( ". {0!r}".format( e))

    print("\n")
    try:
        print( "INVALID: del p1['pcenabled']  ...")
        del p1['pcenabled']
        raise AssertionError( "Invalid key deletion was not detected")
    except TypeError as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( "p1.is_enabled: {0}, p1.disabled_str: {1}"
           .format( p1.is_enabled, p1.disabled_str))
    print( "p2 = Podcast('URL2', 2, 'name2', PCEnabled.Enabled, 7, 23, 45)")
    p2 = Podcast('URL2', 2, 'name2', PCEnabled.Enabled, 7, 23, 45)

    print("\n")
    print( "repr(p2): {0!r}".format(p2))

    print("\n")
    print( "p2.is_enabled: {0}, p2.disabled_str: {1}"
           .format( p2.is_enabled, p2.disabled_str))

    print( """
"INVALID: ep = Episode( 'podcast', 1, 'title', 'url', 'guid', '', \
                 'Pending', -1, 0, None, 0)""")
    try:
        ep = Episode( 'podcast', 1, 'title', 'url', 'guid', '', \
                     'Pending', -1, 0, None, 0)
        raise AssertionError( "Invalid class for ep.podcast was not detected")
    except TypeError as e:
        print( ". {0!r}".format( e))

    print( """
"INVALID: ep = Episode( p1, 1, 'title', 'url', 'guid', '',
                 'Pending', -1, 0, None, 0)""")
    try:
        ep = Episode( p1, 1, 'title', 'url', 'guid', '', \
                     'Pending', -1, 0, None, 0)
        raise AssertionError( "Invalid class for ep.podcast was not detected")
    except TypeError as e:
        print( ". {0!r}".format( e))

    print( """
"ep = Episode( p1, 1, 'title', 'url', 'guid', '',
                 EpisodeStatus.Pending, -1, 0, None, 0)""")
    ep = Episode( p1, 1, 'title', 'url', 'guid', '', \
                 EpisodeStatus.Pending, -1, 0, None, 0)

    print("\n")
    print( "ep.__doc__: {0}".format( ep.__doc__))

    print("\n")
    print( "str(ep): {0!s}".format(ep))

    print("\n")
    print( "repr(ep): {0!r}".format(ep))

    print("""
   DONE.
""")

if __name__ == '__main__':
    # Run test code when invoked on the command line
    sys.exit( test())

