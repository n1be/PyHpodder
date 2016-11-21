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

"""This file implements the update feeds command."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging, sys, time
from optparse import OptionParser
try:
    str = unicode
except NameError:
    pass

# PyPI module feedparser, not in standard library.
try:
    import feedparser
except ImportError:
    print( """
  Error: Module "feedparser" not found. Please install "python-feedparser".
         If this package is not available for your OS, the feedparser
         package can be downloaded from the Python Package Index,
         http://pypi.python.org/pypi/feedparser
""", file=sys.stderr)
    sys.exit(1)

# Other pypod modules
from pypod.lib.config import get_option
from pypod.lib.db import add_episode, get_selected_podcasts, update_podcast
from pypod.lib.datatypes import Episode, EpisodeStatus, PCEnabled
from pypod.lib.url_getter import cached_get
from pypod.lib.utils import generic_id_help, mutex, sanitize_basic


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-07-24"
__license__   = "GPLv3"
__version__   = "0.2"


def _d( msg):
    "Print debugging messages"
    logging.debug( "update: " + str( msg))

def _i( msg):
    logging.info( "update: " + str( msg))

def _w( msg):
    logging.warning( "update: " + str( msg))


_usage_text = "Usage: %prog update [<castid>...]"
_helptext = _usage_text + """

Running update will cause %prog to look at each requested podcast.  This
will download the feed for each enabled podcast and update the database of
available episodes.  It will not actually download any episodes; see the
download command for that.

""" + generic_id_help( "podcast")


feedparser.USER_AGENT = "PyPod/{0} +{1}".format(
    __version__, "http://home.earthlink.net/~n1be/")


def _handle_parse_error( d, pc, gcp, gdbh):
    exc = d.bozo_exception
    if 'getMessage' in dir( exc):
        if 'getLineNumber' in dir( exc):
            _w( "bozo {0} at line {1}".format( exc.getMessage(),
                                               exc.getLineNumber()))
        else:
            _w( "bozo {0}".format( exc.getMessage()))
    else:
        _w( "bozo {0}".format( exc))
    _handle_feed_error( pc, gcp, gdbh)


def _handle_feed_error( pc, gcp, gdbh):
    pc.failedattempts = pc.failedattempts + 1
    # Consider whether to disable this feed
    faildays = int( get_option( gcp, pc.castid, "podcastfaildays"))
    failattempts = int( get_option( gcp, pc.castid, "podcastfailattempts"))
    # If never was updated, just use number of failed attempts...
    lupdate = pc.lastupdate or 0
    time_permits_del = pc.lastattempt - lupdate > faildays * 60 * 60 * 24
    numb_permits_del = pc.failedattempts > failattempts
    _d( "local {0}".format( locals()))
    if numb_permits_del and time_permits_del:
        pc.pcenabled = PCEnabled.ErrorDisabled
        _w( "   Podcast {0.castname} disabled due to errors.".format( pc))
    update_podcast( gdbh, pc)
    gdbh.commit()


def _show_feed_details( d):
    if( d.has_key( 'status')):
        _d( "HTTP status: {0}".format( d.status))
    if( d.has_key( 'href')):
        _d( "HTTP href: {0}".format( d.href))
    if not d.has_key( 'feed'):
        _w( "No feed found")
        return
    f = d.feed
    for k in [ 'title', 'link', 'description', 'date', 'id']:
        if( f.has_key( k)):
            _d( "Feed {0}: {1}".format( k, f[ k]))
    if not d.has_key( 'entries'):
        return
    _d( "{0} entries found:".format( len( d.entries)))
    for ii, item in enumerate( d.entries):
        for k in [ 'title', 'description', 'date', 'id']:
            if( item.has_key( k)):
                _d( ".{0} Item {1}: {2}".format( ii, k, item[ k]))
        if item.has_key( 'enclosures'):
            _d( ".{0} has {1} enclosures".format( ii, len( item.enclosures)))
            for ie, encl in enumerate( item.enclosures):
                for k in [ 'type', 'length', 'href', 'id']:
                    if( encl.has_key( k)):
                        _d( "..{0} Encl {1}: {2}".format( ie, k, encl[ k]))


def _item_to_ep( encl, ie, item, pc):
    "Extract info about one enclosure from the feed"
    if item.has_key( 'title'):
        title = sanitize_basic( item.title).strip()
    else:
        title = ""
    if encl.has_key( 'href'):
        url = sanitize_basic( encl.href).strip()
    else:
        _w( "Missing enclosure URL on {0}".format( title))
        return None
    if item.has_key( 'id'):
        guid = sanitize_basic( item.id).strip()
        if len( item.enclosures) > 1:
            guid += "/{0}".format( ie)
    else:
        guid = ""
    if encl.has_key( 'type'):
        type = sanitize_basic( encl.type).strip()
    else:
        type = "application/octet-stream"
    try:
        length = int( sanitize_basic( encl.length).strip())
    except:
        _d( "defaulting enclosure length to zero.")
        length = 0
    return Episode( podcast=pc, epid=0, eptitle=title, epurl=url, epguid=guid,
                    eptype=type, epstatus=EpisodeStatus.Pending,
                    eplength=length, epfirstattempt=None, eplastattempt=None,
                    epfailedattempts=0)


def _update_enclosure( encl, ie, item, pc, gcp, gdbh):
    "Apply feed info to one enclosure"
    ep = _item_to_ep( encl, ie, item, pc)
    if ep == None:
        return 0
    newc = add_episode( gdbh, ep)
    gdbh.commit()
    return newc


def _update_feed( d, pc, gcp, gdbh):
    "Apply feed info to this podcast"
    if d.has_key( 'entries'):
        count = 0
        for item in d.entries:
            if item.has_key( 'enclosures'):
                for ie, encl in enumerate( item.enclosures):
                    count += _update_enclosure( encl, ie, item, pc, gcp, gdbh)
        if count:
            _i( "Added {0} new episodes".format( count))
    if pc.castname == "" and d.feed.has_key( 'title'):
        pc.castname = sanitize_basic( d.feed.title).strip()


def _update_podcast( pc, gcp, gdbh):
    "update one podcast feed"
    _i( " * Podcast {0.castid}: {0.feedurl}".format( pc))
    pc.lastattempt = int( time.time())
    resp, content = cached_get( pc.feedurl)
    if not resp:
        _handle_feed_error( pc, gcp, gdbh)
        return
    if resp.status == 304:
        # Not changed since last query
        _i( "HTTP status {0.status} - {0.reason}".format( resp))
    else:
      # d = feedparser.parse( pc.feedurl)
        d = feedparser.parse( content)
        if d.bozo:
            _handle_parse_error( d, pc, gcp, gdbh)
            return
        _d( " . feed download complete")
        _show_feed_details( d)
        _update_feed( d, pc, gcp, gdbh)
    pc.lastupdate = int( time.time())
    pc.failedattempts = 0
    update_podcast( gdbh, pc)
    gdbh.commit()


def _update_worker( args, gcp, gdbh):
    "Re-scan enabled feeds and update list of needed downloads"
    parser = OptionParser( usage=_helptext)
    (options, args) = parser.parse_args( args=args)
    podcasts = filter( lambda pc: pc.is_enabled,
                       get_selected_podcasts( gdbh, args))
    _i( "{0} podcast(s) to consider:".format( len( podcasts)))
    for pc in podcasts:
        try:
            _update_podcast( pc, gcp, gdbh)
        except KeyboardInterrupt:
            _i( "Interrupted bu Ctrl-C")
            return


def _cmd_worker( args, gcp, gdbh):
    "Hold database mutex while running the update command"
    with mutex():
        _update_worker( args, gcp, gdbh)


def register_self( reg_callback):
   reg_callback( name="update",
                  descrip="Scan feeds and update list of available downloads",
                  func=_cmd_worker, usage_text=_usage_text)
