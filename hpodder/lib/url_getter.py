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


"""This is the url download utility routines for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function , unicode_literals
import hashlib
import logging
import os
import socket
from urlparse import urlparse
try:
    str = unicode
except NameError:
    pass

# PyPI package
import httplib2

# other hpodder modules
from config import get_feed_cache
from utils import sanitize_filename


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-02-05"
__license__   = "GPL"
__version__   = "0.1"


_debug = 0

if _debug:
    httplib2.debuglevel = 1


_headers = {"User-Agent": "PyHpodder/{0} +{1}".format(
        __version__, "http://home.earthlink.net/~n1be/") }

# httplib2 does not understand unicode cache dirname...
_http = httplib2.Http( get_feed_cache().encode('ascii','ignore'))
_http_no_cache = httplib2.Http()


def _d( msg):
    "Print debugging messages"
    logging.debug( "url: " + str( msg))

def _w( msg):
    "Print debugging messages"
    logging.warning(  msg)


def _common_get_url( http, url):
    "Common code for resource fetch whether or not cacheing is in use."
    _d( "get url: " + url)
    try:
        response, content = http.request( url, headers=_headers)
    except httplib2.HttpLib2Error as e:
        _w( "{0!s}".format( e))
        return None, None
    except ( socket.error, socket.timeout) as e:
        _w( "Socket error: {0!s} at url {1}".format( e, url))
        return None, None
    _d( "response: " + str( response))
    if response.status >= 400:
        _w( "HTTP error status {0.status} - {0.reason}".format( response))
        return None, None
    return response, content


def cached_get( url):
    """Fetch a resource with caching.  This is intended for resources that are
       repeatedly referenced like podcast feeds."""
    return _common_get_url( _http, url)


def easy_get( dir, url):
    """Fetch a resource to a local file without cacheing.  This is intended for
       resources like enclosures that typically only are fetched once."""
    response, content = _common_get_url( _http_no_cache, url)
    if not response:
        return None, None, None
    _d( "content-location: {0}".format( response['content-location']))
    o = urlparse( response['content-location'])
    bef, sep, filename = o.path.rpartition( "/")
    if not filename or filename == "." or filename == "..":
        filename = hashlib.md5( url).hexdigest()
    filename = sanitize_filename( filename)
    _d( "filename: " + filename)
    path = dir + os.sep + hashlib.md5( url).hexdigest()
    with open( path, 'w') as f:
        f.write( content)
    type = response['content-type']
    _d( "type: " + type)
    return filename, path, type


def _test_get( url):
    r, c = cached_get( url)
    if c:
        print( "cached_get len = {0}".format( len( c)))


if __name__ == '__main__':
    # Test code
    logging.basicConfig( level=logging.DEBUG,
                         format="%(levelname)s %(message)s")

    if False:
        print( "GOOD URL")
        _test_get( "http://www.sciam.com/podcast/sciam_podcast_r.xml")
        print()

        url = "http://1.2.3.4/podcast.xml"
        print( "No SuCH HOST, non-DNS URL: " + url)
        _test_get( url)
        print()

        url = "barf.farts"
        print( "BAD URL: " + url)
        _test_get( url)
        print()

        # more rapid timeout for following tests
        _http = httplib2.Http( get_feed_cache().encode('ascii','ignore'), 5)

        url = "http://barf.wildwood/"
        print( "NO SUCH DNS NAME: " + url)
        _test_get( url)
        print()

        url = "http://wildwood.homeip.net/"
        print( "Good hostname but NO SUCH Server: " + url)
        _test_get( url)
        print()

    print( "============================================================")

    if False:
        url = "http://cmdln.evenflow.nl/mp3/cmdln.net_2009-05-20.mp3"
        f, p, t = easy_get( "/tmp", url)
        print( "Result file {0}".format( p))
        print()

        url = "http://www.pbs.org/wgbh/nova/rss/podcast/redir/http://www-tc.pbs.org/wgbh/nova/rss/media/nova_a_pod_machupicchu_100127a.mp3"
        f, p, t = easy_get( "/tmp", url)
        print( "Result file {0}".format( p))
        print()

        url = "http://downloads.bbc.co.uk/podcasts/radio4/material/material_20100204-1800a.mp3"
        f, p, t = easy_get( "/tmp", url)
        print( "Result file {0}".format( p))
        print()

        url = "http://www.pbs.org/wgbh/amex/rss/np/redir/http://www-tc.pbs.org/wgbh/amex/rss/media/presidents_10.mp3"
        f, p, t = easy_get( "/tmp", url)
        print( "Result file {0}".format( p))
        print()

        url = "http://www.scientificamerican.com/podcast/podcast.mp3?e_id=9E8EAAE7-E0AA-61B1-B502EB309A28A85D&ref=p_itune"
        f, p, t = easy_get( "/tmp", url)
        print( "Result file {0}".format( p))
        print()

    # Invalid URL, server returns success
    url = "http://www.scientificamerican.com/podcast/podcast.mp3?e_id=9F8EAAE7-E0AA-61B1-B502EB309A28A85D&ref=p_itune"
    f, p, t = easy_get( "/tmp", url)
    print( "Result file {0}".format( p))
    print()

    # Invalid URL, no such file
    url = "http://www.ibm.com/barf/baz"
    f, p, t = easy_get( "/tmp", url)
    print( "Result file {0}".format( p))
    print()

