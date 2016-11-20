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


"""This is the SQL DB access library for hpodder ported to python.
hpodder was written in Haskell by John Goerzen <http://www.complete.org/>.
Debian GNU/Linux distributes hpodder"""

# standard library imports
from __future__ import print_function, unicode_literals
from itertools import groupby
import logging
try:
    import sqlite3 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite
try:
    str = unicode
except NameError:
    pass

# Other hpodder modules
from config import get_db_path, get_encl_tmp
from ppod_types import *
from utils import empty_dir, exe_name

__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2010 {0}. All rights reserved.".format( __author__)
__date__      = "2010-01-16"
__license__   = "GPL"
__version__   = "0.1"

_debug = 0


def _d( msg):
    "Print db debugging messages"
    logging.debug( "DB: {0!s}".format( msg))

def connect( path=get_db_path()):
    "access the database and update the schema to the current version"
    dbh =  sqlite.connect( path)
    dbh.row_factory = sqlite.Row
    _prep_db( dbh)    
    _d( "DB preparation complete")
    return dbh

def disconnect( dbh):
    "close the database connection"
    dbh.close()

def _prep_db( dbh):
    "Create database and upgrade to latest supported schema"
    if _debug:
        tables = dbh.execute(
            'SELECT name FROM sqlite_master WHERE type = "table"').fetchall()
        dbh.rollback()
        _d( "Existing DB tables are:\n {0!s}".format(
                [ r[0] for r in tables]))
    schemaver = _prep_schema_version( dbh)
    _upgrade_schema( dbh, schemaver)

def _prep_schema_version( dbh):
    "Retrieve schema version and instantiate missing schemaver table"
    try:
        sv = dbh.execute( 'SELECT version FROM schemaver').fetchone()[0]
        dbh.rollback()
    except:
        sv = 0
        _d( "Initializing schemaver to {0}".format( sv))
        dbh.execute('CREATE TABLE schemaver (version INTEGER)')
        dbh.execute('INSERT INTO schemaver VALUES ( :sv)', locals())
        dbh.commit()
    _d( "Discovered schemaver {0}".format( sv))
    return sv

def _set_db_schema_version( dbh, sv):
    "Change the schema version recorded in the db"
    _d( ".setting schema version in db to {0}".format( sv))
    dbh.execute( 'UPDATE schemaver SET version = :sv', locals())

def _upgrade_schema( dbh, schemaver):
    "Upgrade the database to the PyHpodder current schema version"
    sv = schemaver

    if sv == 0:
        sv = sv + 1
        _d( "Upgrading database schema to version {0}".format( sv))
        _d( '.creating "podcasts" table')
        dbh.execute( """CREATE TABLE podcasts
                        ( castid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                          castname TEXT NOT NULL,
                          feedurl TEXT NOT NULL UNIQUE)""")
        _d( '.creating "episodes" table')
        dbh.execute( """CREATE TABLE episodes
                        ( castid INTEGER NOT NULL,
                          episodeid INTEGER NOT NULL,
                          title TEXT NOT NULL,
                          epurl TEXT NOT NULL,
                          enctype TEXT NOT NULL,
                          status TEXT NOT NULL,
                          UNIQUE( castid, epurl),
                          UNIQUE( castid, episodeid) )""")
        _set_db_schema_version( dbh, sv)
        dbh.commit()

    if sv == 1:
        sv = sv + 1
        _d( "Upgrading database schema to version {0}".format( sv))
        _d( '.adding "pcenabled" and "lastupdate" columns')
        dbh.executescript( """ALTER TABLE podcasts
                                  ADD pcenabled INTEGER NOT NULL DEFAULT 1;
                              ALTER TABLE podcasts
                                  ADD lastupdate INTEGER;""")
        _set_db_schema_version( dbh, sv)
        dbh.commit()

    if sv == 2:
        sv = sv + 1
        _d( "Upgrading database schema to version {0}".format( sv))
        _d( '.adding "eplength" column')
        dbh.execute( """ALTER TABLE episodes
                            ADD eplength INTEGER NOT NULL DEFAULT 0""")
        _set_db_schema_version( dbh, sv)
        dbh.commit()
        # Empty the enclosure storage since our naming changed when this
        # version arrived
        empty_dir( get_encl_tmp())

    if sv == 3:
        sv = sv + 1
        _d( "Upgrading database schema to version {0}".format( sv))
        _d( ".adding podcasts columns:"
            " lastattempt, failedattempts")
        _d( ".adding episodes columns:"
            " epfirstattempt, eplastattempt, epfailedattempts")
        dbh.executescript(
            """ALTER TABLE podcasts
                   ADD lastattempt INTEGER;
               ALTER TABLE podcasts
                   ADD failedattempts INTEGER NOT NULL DEFAULT 0;
               ALTER TABLE episodes
                   ADD epfirstattempt INTEGER;
               ALTER TABLE episodes
                   ADD eplastattempt INTEGER;
               ALTER TABLE episodes
                   ADD epfailedattempts INTEGER NOT NULL DEFAULT 0;""")
        _set_db_schema_version( dbh, sv)
        dbh.commit()

    if sv == 4:
        sv = sv + 1
        _d( "Upgrading database schema to version {0}".format( sv))
        _d( ".re-creating episodes table to add epguid column"
            " and UNIQUE constaint")
        dbh.executescript( """CREATE TABLE episodes5
                                ( castid INTEGER NOT NULL,
                                  episodeid INTEGER NOT NULL,
                                  title TEXT NOT NULL,
                                  epurl TEXT NOT NULL,
                                  enctype TEXT NOT NULL,
                                  status TEXT NOT NULL,
                                  eplength INTEGER NOT NULL DEFAULT 0,
                                  epfirstattempt INTEGER,
                                  eplastattempt INTEGER,
                                  epfailedattempts INTEGER NOT NULL DEFAULT 0,
                                  epguid TEXT,
                                  UNIQUE(castid, epurl),
                                  UNIQUE(castid, episodeid),
                                  UNIQUE(castid, epguid) );

                              INSERT INTO episodes5
                                  SELECT *, NULL FROM episodes;

                              DROP TABLE episodes;

                              ALTER TABLE episodes5
                                  RENAME TO episodes;""")
        _set_db_schema_version( dbh, sv)
        dbh.commit()

    if sv == 5:
        _d( "At current supported database schema version: {0}".format( sv))
        pass

    else:
        raise ValueError( """Unrecognized database schema version: {0}
You probably need a newer {1} to read this database.""".format( sv, exe_name()))


def add_podcast( dbh, pc):
    """ Add a new podcast to the database.
This ignores the castid on the incomingd podcast,
and returns a new object with the castid populated.
A duplicate add is an error."""
    try:
        dbh.execute( """INSERT INTO podcasts
                            ( castname, feedurl, pcenabled, lastupdate,
                              lastattempt, failedattempts)
                            VALUES ( ?, ?, ?, ?, ?, ?)""",
                            ( pc.castname, pc.feedurl,
                              pc.pcenabled.index, pc.lastupdate,
                              pc.lastattempt, pc.failedattempts) )
        r = dbh.execute( 'SELECT castid FROM podcasts WHERE feedurl = :feedurl',
                         pc ).fetchone()[0]
        pc.castid = r
        return pc
    except:
        print( "Error adding feed {0.feedurl}\nPerhaps this URL already exists?".format( pc))
        raise

def _podcast_convrow( row):
    "Convert row from database to instance of class Podcast"
    return Podcast(
        castid		= row['castid'.encode('ascii','ignore')],
        castname	= row['castname'.encode('ascii','ignore')],
        feedurl		= row['feedurl'.encode('ascii','ignore')],
        pcenabled	= PCEnabled[ row['pcenabled'.encode('ascii','ignore')]],
        lastupdate	= row['lastupdate'.encode('ascii','ignore')],
        lastattempt	= row['lastattempt'.encode('ascii','ignore')],
        failedattempts	= row['failedattempts'.encode('ascii','ignore')])

def get_all_podcasts( dbh):
    """Return a list of all podcasts."""
    res = dbh.execute( "SELECT * FROM podcasts ORDER BY castid").fetchall()
    return map( _podcast_convrow, res)

def get_selected_podcasts( dbh, wanted_ids):
    """Return a list of selected podcasts."""
    if (len( wanted_ids) == 0) or ( wanted_ids[0] == 'all'):
        return get_all_podcasts( dbh)
    res = []
    for pcid, grp in groupby( sorted( wanted_ids)): # eliminates duplicates
        pc = dbh.execute( "SELECT * FROM podcasts WHERE castid = :pcid",
                          locals()).fetchone()
        if pc != None:
            res.append( _podcast_convrow( pc))
    return res

def update_podcast( dbh, pc):
    """Update one podcast row in the database
    The podcast row must already exist else the update request is ignored."""
    dbh.execute( """UPDATE podcasts
                      SET castname = ?, feedurl = ?, pcenabled = ?,
                          lastupdate = ?, lastattempt = ?, failedattempts = ?
                      WHERE castid = ?""",
                 ( pc.castname, pc.feedurl, pc.pcenabled.index, pc.lastupdate,
                   pc.lastattempt, pc.failedattempts, pc.castid) )


def remove_podcast( dbh, pc):
    "Remove a podcast and related episodes from the database."
    pcid = pc.castid
    dbh.execute( 'DELETE FROM episodes WHERE castid = :pcid', locals())
    dbh.execute( 'DELETE FROM podcasts WHERE castid = :pcid', locals())
    _d( "Vacuuming")
    dbh.execute( 'VACUUM')

## --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -- 

def _episode_convrow( pc, row):
    "Convert row from database to instance of class Episode"
    return Episode(
        podcast =          pc,
        epid =             row['episodeid'.encode('ascii','ignore')],
        eptitle =          row['title'.encode('ascii','ignore')],
        epurl =            row['epurl'.encode('ascii','ignore')],
        epguid =           row['epguid'.encode('ascii','ignore')],
        eptype =           row['enctype'.encode('ascii','ignore')],
        epstatus = string_to_enum(
                       row['status'.encode('ascii','ignore')], EpisodeStatus),
        eplength =         row['eplength'.encode('ascii','ignore')],
        epfirstattempt =   row['epfirstattempt'.encode('ascii','ignore')],
        eplastattempt =    row['eplastattempt'.encode('ascii','ignore')],
        epfailedattempts = row['epfailedattempts'.encode('ascii','ignore')])

def get_all_pc_episodes( dbh, pc):
    """Return a list of all episodes for one podcast."""
    pcid = pc.castid
    res = dbh.execute(
        "SELECT * FROM episodes WHERE castid = :pcid ORDER BY episodeid",
        locals()).fetchall()
    return map( lambda row: _episode_convrow( pc, row), res)

def get_selected_pc_episodes( dbh, pc, wanted_ids):
    """Return a list of selected episodes for one podcast."""
    if (len( wanted_ids) == 0) or ( wanted_ids[0] == 'all'):
        return get_all_pc_episodes( dbh, pc)
    pcid = pc.castid
    res = []
    for epid, grp in groupby( sorted( wanted_ids)): # eliminates duplicates
        ep = dbh.execute( """SELECT * FROM episodes
                                 WHERE castid = :pcid AND episodeid = :epid""",
                          locals()).fetchone()
        if ep != None:
            res.append( _episode_convrow( pc, ep))
    return res

def add_episode( dbh, ep): 
    """ Add a new episode. If the episode already exists, based solely on
    looking at the GUID (if present), update the URL and title fields.
    Returns the number of inserted rows."""
    # We have to be careful of cases where a feed may have two
    # different episodes with different GUIDs but identical URLs.
    # So if we have a GUID match here, we must have a conflict on URL,
    # so we ignore the request to change it.
    if ep.epguid != '':
        cur = dbh.execute( """UPDATE OR IGNORE episodes
                                  SET epurl = ?, title = ?, epguid = ?
                                  WHERE castid = ? AND
                                       ( epguid = ? OR epurl = ?)""",
                           ( ep.epurl, ep.eptitle, ep.epguid,
                             ep.podcast.castid, ep.epguid, ep.epurl) )
        if cur.rowcount > 0:
            # if the UPDATE was successful, that means that something with the
            # same GUID already exists, so the INSERT below will be ignored.
            _d( "update done")
            return 0
    max_epid = dbh.execute(
                         'SELECT MAX(episodeid) FROM episodes WHERE castid = ?',
                           ( ep.podcast.castid,)).fetchone()[0]
    next_epid = (max_epid or 0) + 1
    _d( "add_episode: new epid: {0}".format( next_epid))
    ep.epid = next_epid
    _update_episodes_table( "INSERT OR IGNORE", dbh, ep)
    return 1

def update_episode( dbh, ep):
    "Update an episode.  If it doesn't already exist, create it."
    _update_episodes_table( "INSERT OR REPLACE", dbh, ep)

def _update_episodes_table( insertsql, dbh, episode):
    """Privately used common SQL for insert to or update episodes table"""
    dbh.execute( insertsql + """ INTO episodes (castid, episodeid, title,
                   epurl, enctype, status, eplength, epfirstattempt,
                   eplastattempt, epfailedattempts, epguid)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 ( episode.podcast.castid, episode.epid, episode.eptitle,
                   episode.epurl, episode.eptype,
                   episode.epstatus.__str__(),
                   episode.eplength, episode.epfirstattempt,
                   episode.eplastattempt, episode.epfailedattempts,
                   episode.epguid ) )



if __name__ == "__main__":
    # Test code to run when invoked on the command line
    print( __doc__)
    print()
    _debug = 1
    logging.basicConfig( level=logging.DEBUG,
                         format="%(levelname)s %(message)s")

    print( "\n*** Open new database:")
    dbh = connect( ":memory:")

    print( "\n*** Prepare existing database:")
    _prep_db( dbh)

    print( "\n*** Add podcasts, getting unique castid:")
    p1 = Podcast( 0, 'name1', 'URL1', PCEnabled.ErrorDisabled, 7)
    p2 = Podcast( 0, 'name2', 'URL2', PCEnabled.Enabled, 8, 23, 45)
    print( ". before:\n.. {0}\n.. {1}".format( p1, p2))
    p1 = add_podcast( dbh, p1)
    p2 = add_podcast( dbh, p2)
    print( ". after :\n.. {0}\n.. {1}".format( p1, p2))

    try:
        print( "\n*** Add duplicate podcast ...")
        add_podcast( dbh, p1)
    except Exception as e:
        print( ". {0!r}".format( e))

    print( "\n*** get_selected_podcasts( [ 3, 2, 0]):")
    for p in get_selected_podcasts( dbh, [ 3, 2, 0]):
        print(". {0}".format( p))

    print( "\n*** get_selected_podcasts( [ 2, 1, 2, 1]):")
    for p in get_selected_podcasts( dbh, [ 2, 1, 2, 1]):
        print(". {0}".format( p))

    print( "\n*** Update podcast 1:")
    p13 = Podcast( 1, 'name3', 'URL3', PCEnabled.UserDisabled, 27, 89, 15)
    update_podcast( dbh, p13)

    print( "\n*** Get all podcasts ...")
    for p in get_all_podcasts( dbh):
        print(". {0!r}".format( p))

    print( "\n*** Add Episode ...")
    ep1 = Episode( p13, 1, "ep1title", "ep1url", "", "application/mp3",
                   EpisodeStatus.Pending, 100)
    n=add_episode( dbh, ep1)
    print( "add_episode returns {0} for {1!r}".format( n, ep1))

    print( "\n*** Add the same Episode again ...")
    n=add_episode( dbh, ep1)
    print( "add_episode returns {0} for {1}".format( n, ep1))

    print( "\n*** Add another Episode with an epguid...")
    ep12 = Episode( p13, 2, "ep12title", "ep12url", "ep12guid", "application/mp3",
                   EpisodeStatus.Pending, 1200)
    n=add_episode( dbh, ep12)
    print( "add_episode returns {0} for {1}".format( n, ep12))

    print( "\n*** Again add epguid Episode with modified title and URL ...")
    ep12.eptitle = "ep122title"
    ep12.epurl = "ep122url"
    n=add_episode( dbh, ep12)
    print( "add_episode returns {0} for {1}".format( n, ep12))

    print( "\n*** Change epstatus using update_episode ...")
    ep1.epstatus = EpisodeStatus.Downloaded
    update_episode( dbh, ep1)

    print( "\n*** Add episode to pc2 using update_episode ...")
    ep2 = Episode( p2, 1, "ep21title", "ep21url", "", "application/mp3",
                   EpisodeStatus.Pending, 2100)
    update_episode( dbh, ep2)

    print( "\n*** Get selected (\"all\") podcasts ...")
    for p in get_selected_podcasts( dbh, ["all"]):
        print(". {0!s}".format( p))

    print( "\n*** Dump database contents ...")
    for line in dbh.iterdump():
        if line.startswith( "INSERT "):
            print( line)

    print( "\n*** All episodes from podcast 3 ...")
    pc = Podcast( 3, '', '', PCEnabled.Enabled, 7)
    print( get_all_pc_episodes( dbh, pc))

    print( "\n*** All episodes from podcast 2 ...")
    pc.castid = 2
    print( get_all_pc_episodes( dbh, pc))

    print( "\n*** Selected [] episodes from podcast 1 ...")
    pc.castid = 1
    for e in get_selected_pc_episodes( dbh, pc, []):
        print( str( e))

    print( "\n*** Selected ['all'] episodes from podcast 1 ...")
    pc.castid = 1
    for e in get_selected_pc_episodes( dbh, pc, [ 'all']):
        print( str( e))

    print( "\n*** Selected [ 0, 2, 4, 6] episodes from podcast 1 ...")
    pc.castid = 1
    for e in get_selected_pc_episodes( dbh, pc, [ 0, 2, 4, 6]):
        print( str( e))

    print( "\n*** Remove podcast #1 ...")
    remove_podcast( dbh, p1)

    print( "\n*** Get selected (\"[]\") podcasts ...")
    for p in get_selected_podcasts( dbh, []):
        print(". {0!s}".format( p))

    print( "\n*** Dump database contents ...")
    for line in dbh.iterdump():
        if line.startswith( "INSERT "):
            print( line)

    print( "\n***database disconnect:")
    disconnect( dbh)

    print( "***database test complete")
