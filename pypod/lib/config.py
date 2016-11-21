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

"""This file handles reading and writing the configuration.  For upward
compatability, the configuration is stored in ~/.hpodder/hpodder.conf.
  This file also defines the default configuration.  Some values such as
the location of the application working directories and files, are hard
coded in functions below."""


# standard library imports
from __future__ import print_function, unicode_literals
import ConfigParser
import os
try:
    str = unicode
except NameError:
    pass

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-08-09"
__license__   = "GPLv3"
__version__   = "0.2"


def get_app_dir():
    """Returns path to application's data directory"""
    # Use the following line for development / debugging
    # return os.path.expanduser("~") + os.sep + ".hpodder_dev"
    return os.path.expanduser("~") + os.sep + ".hpodder"


def get_encl_tmp():
    """Returns path to application's enclosure storage directory"""
    return get_app_dir() + os.sep + "enclosurexfer"


def get_feed_cache():
    """Returns path to application's feed cache directory"""
    return get_app_dir() + os.sep + "feedcache"


def get_db_path():
    """Returns path to application's database file"""
    return get_app_dir() + os.sep + "hpodder.db"


def get_config_path():
    """Returns path to application's configuration file"""
    return get_app_dir() + os.sep + "hpodder.conf"


def get_default_config():
    """Returns a configuration object containing default settings"""
    downloaddir = os.path.expanduser("~") + os.sep + "podcasts"
    cp = ConfigParser.SafeConfigParser()
    cp.add_section( "general")
    cp.set( "general", "showintro", "yes")
    cp.set( "DEFAULT", "downloaddir", downloaddir)
    cp.set( "DEFAULT", "namingpatt", "%(safecasttitle)s/%(safefilename)s")
    cp.set( "DEFAULT", "maxthreads", "2")
    cp.set( "DEFAULT", "progressinterval", "1")
    cp.set( "DEFAULT", "podcastfaildays", "21")
    cp.set( "DEFAULT", "podcastfailattempts", "15")
    cp.set( "DEFAULT", "epfaildays", "21")
    cp.set( "DEFAULT", "epfailattempts", "15")
    cp.set( "DEFAULT", "renametypes",
            "audio/mpeg:.mp3,audio/mp3:.mp3,x-audio/mp3:.mp3")
    cp.set( "DEFAULT", "postproctypes", "audio/mpeg,audio/mp3,x-audio/mp3")
    cp.set( "DEFAULT", "gettypecommand", "file -b -i \"${EPFILENAME}\"")
    cp.set( "DEFAULT", "postproccommand",
            "mid3v2 -A \"${CASTTITLE}\" -t \"${EPTITLE}\" -T ${EPID}" +
            " --WOAF \"${EPURL}\" --WOAS \"${FEEDURL}\" \"${EPFILENAME}\"")
    return cp


def load_config():
    """Returns a configuration object with the current settings"""
    cpname = get_config_path()
    defaultcp = get_default_config()
    if os.path.exists( cpname):
        cp = defaultcp
        cp.readfp( open( cpname))
        return cp
    else:
        return defaultcp


def store_config( cp):
    """Write the supplied info to the user's configuration file"""
    cp.write( get_config_path())


def get_max_threads():
    """Returns the integer max_threads value in the configuration"""
    return load_config().getint( "general", "maxthreads")


def get_progress_interval():
    """Returns the integer progress_interval value in the configuration"""
    return load_config().getint( "general", "progressinterval")


def get_option( cp, sect, key, vars={}):
    """Returns the string value of one configured option"""
    try:
        return cp.get( str( sect), key, vars=vars)
    except ConfigParser.NoSectionError:
        return cp.get( "DEFAULT", key, vars=vars)
