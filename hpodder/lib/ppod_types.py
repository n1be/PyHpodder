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


"""This is the application-specific datatypes for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function, unicode_literals
try:
    str = unicode
except NameError:
    pass

# PyPI package enum, not available Ubuntu repository, but it is in Fedora
import enum


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-03"
__license__   = "GPL"
__version__   = "0.1"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)


# Enum of episode status values
EpisodeStatus = enum.Enum( 'Pending',	# Ready to download
                        'Downloaded',	# Already downloaded
                        'Error',	# Error downloading
                        'Skipped')	# Skipped by some process

# Enum of whether podcast is enabled
PCEnabled = enum.Enum( 'UserDisabled', 'Enabled', 'ErrorDisabled')

def string_to_enum( str, type):
    if str not in type:
        raise AttributeError( "{0!s} object has no attribute '{1!s}'"
                              .format( type, str))
    exec "choice = type.{0}".format( str)
    return choice


class _AppDict( dict):
    """Dictionary-like superclass for application datatypes"""

    def __repr__( self):
        str = ""
        for key in self:
            str = "{0}, {1!s}:{2!r}".format( str, key, self[key])
        return "{0!s}({1})".format(self.__class__, str[1:])

    def __getattribute__( self, name):
        try:
            return self[name]
        except:
            return super( _AppDict, self).__getattribute__( name)

    def __setattr__( self, name, value):
        try:
            self[ name] = value;
        except KeyError:
           super( _AppDict, self).__setattr__(  name, value)

    def __setitem__( self, key, value):
        if key not in self:
            raise KeyError( "'{0!s}' object has no member '{1!s}'"
                            .format( self.__class__, key))
        if ( type( value) == type( self[ key])) or \
           ( (self[ key] == None) and (type( value) == int)):
            super( _AppDict, self).__setitem__( key, value)
        else:
            raise TypeError( "{0!s}['{1!s}'] cannot store type '{2!s}'"
                             .format( self.__class__, key, type( value)))

    def __delitem__( self, key):
        raise AssertionError( "Can not delete members from {0!s}"
                              .format( self.__class__))


class Podcast( _AppDict):
    """Data about feeds that have been subscribed
    { castid :: Integer,
      castname :: String,
      feedurl :: String,
      pcenabled :: PCEnabled,
      lastupdate :: Maybe Integer, -- Last successful update
      lastattempt :: Maybe Integer,      -- Last attempt
      failedattempts :: Integer}   -- failed attempts since last success
    deriving (Eq, Show, Read) """

    def __init__( self, castid, castname, feedurl, pcenabled, failedattempts,
                  lastupdate=None, lastattempt=None):

        # First initialize dict to establish datatypes
        super( Podcast, self).__init__( castid=0, castname='', feedurl='',
                                        pcenabled=PCEnabled.Enabled, lastupdate=None,
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
        else:
            return "[{0}] ".format( 
                self.pcenabled == PCEnabled.UserDisabled and "disabled" or
                self.pcenabled == PCEnabled.ErrorDisabled and
                "disabled by errors")

    def __str__( self):
        return "Podcast {0} {1}{2}".format( self.castid, self.disabled_str,
                                             self.castname)


class Episode( _AppDict):
    """Data about one enclosure/attachment
    {podcast :: Podcast,
     epid :: Integer,
     eptitle :: String,
     epurl :: String,
     epguid :: Maybe String,
     eptype :: String,
     epstatus :: EpisodeStatus,
     eplength :: Integer,
     epfirstattempt :: Maybe Integer, -- Last successful updat
     eplastattempt :: Maybe Integer, -- Last attempt
     epfailedattempts :: Integer}
deriving (Eq, Show, Read) """

    def __init__( self, podcast, epid, eptitle, epurl, epguid, eptype,
                  epstatus, eplength, epfirstattempt=None, eplastattempt=None,
                  epfailedattempts=0):
        if type( podcast) != Podcast:
            raise TypeError( "'podcast' must be member of class Podcast")
            
        # Initialize dict to establish datatypes
        super( Episode, self).__init__( podcast=podcast, epid=0, eptitle='',
            epurl='', epguid='', eptype='', epstatus=EpisodeStatus.Pending,
            eplength=0, epfirstattempt=None, eplastattempt=None,
            epfailedattempts=0)

        for mbr in ( 'podcast', 'epid', 'eptitle', 'epurl', 'epguid', 'eptype',
                     'epstatus', 'eplength', 'epfirstattempt', 'eplastattempt',
                     'epfailedattempts'):
            exec ( "self[ '{0}'] = {0}".format( mbr))

    def __str__( self):
        return "{0.podcast.castid:5d} {0.epid:5d} {0.epstatus!s:4.4} {0.eptitle}" \
                .format( self)



if __name__ == '__main__':
    # Test code to run when invoked on the command line
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
    print( 'repr( string_to_enum( "Pending", EpisodeStatus)) =',
            repr( string_to_enum( "Pending", EpisodeStatus)))
    try:
        print( 'INVALID: repr( string_to_enum( "Baz", EpisodeStatus)) ...')
        repr( string_to_enum( "Baz", EpisodeStatus))
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: EpisodeStatus[4] ...")
        EpisodeStatus[4]
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: EpisodeStatus.Foo ...")
        EpisodeStatus.Foo
    except Exception as e:
        print( ". {0!r}".format( e))

    print("\n")
    print( 'PCEnabled: ' + PCEnabled.__doc__)
    print( 'for i in PCEnabled:')
    print( '  print i.index, str(i)')
    for i in PCEnabled:
        print( ". {0.index!s} {0!s}".format( i))

    print("\n")
    print( "p1 = Podcast(1, 'name1', 'URL1', PCEnabled.ErrorDisabled, 7)")
    p1 = Podcast(1, 'name1', 'URL1', PCEnabled.ErrorDisabled, 7)
    print( "p1.__doc__: {0}".format( p1.__doc__))
    print( "str(p1): {0!s}".format(p1))
    print( "repr(p1): {0!r}".format(p1))
    print( "p1.castid: {0}".format( p1.castid))
    try:
        print( "INVALID: p1.foo ...")
        p1.foo
    except Exception as e:
        print( ". {0!r}".format( e))
    print( "p1.castid = 6")
    p1.castid = 6
    print( "p1.castid: {0}".format( p1.castid))
    try:
        print( "INVALID: p1.foo = 9 ...")
        p1.foo = 9
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: p1.castid = '9' ...")
        p1.castid = '9'
    except Exception as e:
        print( ". {0!r}".format( e))
    print( "p1.lastupdate = 99")
    p1.lastupdate = 99
    print( "p1.lastupdate: {0}".format( p1.lastupdate))
    try:
        print( "INVALID: delattr(p1, 'foobar')  ...")
        delattr(p1, 'foobar')
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: del p1.lastupdate  ...")
        del p1.lastupdate
    except Exception as e:
        print( ". {0!r}".format( e))

    print( "p1['feedurl'] = 'different_URL'")
    p1['feedurl'] = 'different_URL'
    print( "p1['feedurl']: {0}".format( p1['feedurl']))
    try:
        print( "INVALID: p1['baz']  ...")
        p1['baz']
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: p1['baz'] = 'foo' ...")
        p1['baz'] = 'foo'
    except Exception as e:
        print( ". {0!r}".format( e))
    try:
        print( "INVALID: del p1['pcenabled']  ...")
        del p1['pcenabled']
    except Exception as e:
        print( ". {0!r}".format( e))
    print( "p1.is_enabled: {0}, p1.disabled_str: {1}"
           .format( p1.is_enabled, p1.disabled_str))
    print( "p2 = Podcast(2, 'name2', 'URL2', PCEnabled.Enabled, 7, 23, 45)")
    p2 = Podcast(2, 'name2', 'URL2', PCEnabled.Enabled, 7, 23, 45)
    print( "repr(p2): {0!r}".format(p2))
    print( "p2.is_enabled: {0}, p2.disabled_str: {1}"
           .format( p2.is_enabled, p2.disabled_str))
