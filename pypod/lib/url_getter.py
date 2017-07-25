#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, 2016 Robert N. Evans

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


"""This file implements url download utility routines ."""

# standard library imports
from __future__ import print_function , unicode_literals
import hashlib
import logging
import os
import socket
import sys
from urlparse import urlparse
try:
    str = unicode
except NameError:
    pass

# PyPI module httplib2, not in standard library.
try:
    import httplib2
except ImportError:
    print( """
  Error: Module "httplib2" not found. Please install "python-httplib2".
         If this package is not available for your OS, the httplib2
         package can be downloaded from the Python Package Index,
         http://pypi.python.org/pypi/httplib2
""", file=sys.stderr)
    sys.exit(1)

# other pypod modules
from config import get_feed_cache
from utils import sanitize_filename


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014-2016 {0}. All rights reserved.".format( __author__)
__date__      = "2016-06-17"
__license__   = "GPLv3"
__version__   = "0.5.1"


_debug = 0
_socket_timeout = 120 # seconds

if _debug:
    httplib2.debuglevel = 1


_headers = {"User-Agent": "PyPod/{0} +{1}".format(
        __version__, "http://home.earthlink.net/~n1be/") }

# httplib2 does not understand unicode cache dirname...
_http = httplib2.Http( get_feed_cache().encode('ascii','ignore'),
                       timeout=_socket_timeout)
_http_no_cache = httplib2.Http( timeout=_socket_timeout)


def _d( msg):
    "Print debugging messages"
    logging.debug( "url: " + str( msg))

def _w( msg):
    "Print warning messages"
    logging.warning(  msg)


def _common_get_url( http, url):
    "Common code for resource fetch whether or not cacheing is in use."
    _d( "get url: " + url)
    try:
        http.follow_all_redirects = True
        # http.force_exception_to_status_code = True
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


def easy_get( enc_dir, url):
    """Fetch a resource to a local file without cacheing.  This is intended for
       resources like enclosures that typically only are fetched once."""
    response, content = _common_get_url( _http_no_cache, url)
    if not response:
        return None, None, None
    try:
        _d( "content-location: {0}".format( response['content-location']))
        o = urlparse( response['content-location'])
        bef, sep, filename = o.path.rpartition( "/")
    except:
        filename = None
    if not filename or filename == "." or filename == "..":
        filename = hashlib.md5( url).hexdigest()
    filename = sanitize_filename( filename)
    _d( "filename: " + filename)
    path = enc_dir + os.sep + hashlib.md5( url).hexdigest()
    with open( path, 'w') as f:
        f.write( content)
    mime_type = response['content-type']
    _d( "type: " + mime_type)
    return filename, path, mime_type


def _test_get( url):
    r, c = cached_get( url)
    if c:
        print( "cached_get len = {0}".format( len( c)))

## --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -- 

def test():
    "Test code to run when invoked on the command line"
    print( __doc__)
    print()
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


if __name__ == '__main__':
    # Run test code when invoked on the command line
    sys.exit( test())

