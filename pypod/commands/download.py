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

"""This file implements the download episodes command."""

# standard library imports
from __future__ import print_function, unicode_literals
import logging
from optparse import OptionParser
import os
import os.path
import shutil
import subprocess
import time
import traceback
try:
    str = unicode
except NameError:
    pass

# Other pypod modules
from pypod.lib.config import get_encl_tmp, get_option
from pypod.lib.db import get_selected_podcasts, get_all_pc_episodes, update_episode
from pypod.lib.datatypes import EpisodeStatus, PCEnabled
from pypod.lib.url_getter import easy_get
from pypod.lib.utils import generic_id_help, mutex, sanitize_filename


__author__    = "Robert N. Evans <http://home.earthlink.net/~n1be/>"
__copyright__ = "Copyright (C) 2014 {0}. All rights reserved.".format( __author__)
__date__      = "2014-09-20"
__license__   = "GPLv3"
__version__   = "0.3"

_debug = 1

def _d( msg):
    "Print debugging messages"
    logging.debug( "d/l: " + str( msg))

def _i( msg):
    "Print informational messages"
    logging.info( "d/l: " + str( msg))

def _w( msg):
    "Print warning messages"
    logging.warning( "d/l: " + str( msg))


_usage_text = "Usage: %prog download [<castid>...]"
_helptext = _usage_text + """

The download command will cause %prog to download any podcast
episodes that are marked Pending.  Such episodes are usually generated
by a prior call to "%prog update".  If you want to combine an update
with a download, as is normally the case, you may want "%prog fetch".

""" + generic_id_help( "podcast")


def _handle_episode_error( ep, gcp, gdbh):
    ep.epfailedattempts = ep.epfailedattempts + 1
    # Consider whether to disable this episode
    faildays = int( get_option( gcp, ep.podcast.castid, "epfaildays"))
    failattempts = int( get_option( gcp,ep.podcast.castid, "epfailattempts"))
    time_permits_disable = ep.eplastattempt - ep.epfirstattempt > \
                           faildays * 60 * 60 * 24
    numb_permits_disable = ep.epfailedattempts > failattempts
    _d( "local {0}".format( locals()))
    if numb_permits_disable and time_permits_disable:
        ep.epstatus = EpisodeStatus.Error
        msg = " *** {0.podcast.castid}.{0.episodeid}: Disabled due to errors"
    else:
        msg = " *** {0.podcast.castid}.{0.episodeid}: Error downloading"
    _w( msg.format( ep))
    update_episode( gdbh, ep)
    gdbh.commit()


def _download_episode( ep, gcp, gdbh):
    "Download one pending episode"
    _i( "{0.podcast.castid}.{0.episodeid} {0.title}".format( ep))
    ep.eplastattempt = int( time.time())
    ep.epfirstattempt = ep.epfirstattempt or ep.eplastattempt
    filename, path, content_type = easy_get( get_encl_tmp(), ep.epurl)
    if not path:
        return _handle_episode_error( ep, gcp, gdbh)
    _d( " . {0} episode {1} downloaded".format( content_type, path))
    vars = dict( # These values may be interpolated into config options;
                 # NOTE: config_parser requires these values to be strings:
                 castid="{0.podcast.castid:03d}".format( ep),
                 epid="{0.episodeid:04d}".format( ep),
                 safecasttitle=sanitize_filename( ep.podcast.castname),
                 safeeptitle=sanitize_filename( ep.title),
                 safefilename=sanitize_filename( filename) )
    newfn = (get_option( gcp, ep.podcast.castid,
                         "downloaddir", vars=vars).strip()
             + os.sep +
             get_option( gcp, ep.podcast.castid,
                         "namingpatt", vars=vars).strip())
    # Could use gettypecommand here as the authority on file content type
    if not content_type.strip():
        content_type = ep.enctype.strip()
    # Rename the file to agree with content_type
    for rt in get_option( gcp, ep.podcast.castid, "renametypes").split(","):
        type, sep, suffix = rt.partition( ":")
        if content_type == type:
            if not newfn.endswith( suffix):
                newfn += suffix
            break
    # Move file to final location
    dir = os.path.dirname( newfn)
    os.path.isdir( dir) or os.makedirs( dir)
    shutil.move( path, newfn)
    # Execute post-process command
    env = os.environ
    env[ "CASTID"] = str( ep.podcast.castid)
    env[ "CASTTITLE"] = ep.podcast.castname.encode( 'utf-8')
    env[ "EPFILENAME"] = newfn
    env[ "EPID"] = str( ep.episodeid)
    env[ "EPTITLE"] = ep.title.encode( 'utf-8')
    env[ "EPURL"] = ep.epurl
    env[ "FEEDURL"] = ep.podcast.feedurl
    env[ "SAFECASTTITLE"] = sanitize_filename( ep.podcast.castname)
    env[ "SAFEEPTITLE"] = sanitize_filename( ep.title)
    cmd = get_option( gcp, ep.podcast.castid, "postproccommand").strip()
    if cmd:
        _d( "Postprocess cmd: {0}\n ENV: {1}".format( cmd, env))
        p = subprocess.Popen(args=cmd, close_fds=True, shell=True, env=env)
        _d( "Postprocess cmd started")
        p.wait()
        _d( "Postprocess cmd done, returncode={0}".format( p.returncode))
        if p.returncode:
            _w( "Post-Process command exit status: {0}".format( p.returncode))
    # Update episode status
    ep.epstatus = EpisodeStatus.Downloaded
    update_episode( gdbh, ep)
    gdbh.commit()


def _download_worker( args, gcp, gdbh):
    "Download pending episodes from enabled feeds"
    parser = OptionParser( usage=_helptext)
    (options, args) = parser.parse_args( args=args)
    podcasts = filter( lambda pc: pc.is_enabled,
                       get_selected_podcasts( gdbh, args))
    episodes = []
    for pc in podcasts:
        episodes.extend(
            filter( lambda e: e.epstatus == EpisodeStatus.Pending,
                    get_all_pc_episodes( gdbh, pc)))
    _i( "{0} episode(s) to consider from {1} podcast(s)".format(
            len( episodes), len( podcasts)))
    for ep in episodes:
        try:
            _download_episode( ep, gcp, gdbh)
        except KeyboardInterrupt:
            _i( "Interrupted by Ctrl-C")
            return
        except:
            # Print error and try next episode
            traceback.print_exc()
            continue


def _cmd_worker( args, gcp, gdbh):
    "Hold database mutex while running the download command"
    with mutex():
        _download_worker( args, gcp, gdbh)


def register_self( reg_callback):
   reg_callback( name="download",
                 descrip="Downloads pending podcast episodes (run update first)",
                 func=_cmd_worker, usage_text=_usage_text)
"""
============

cmd_worker gi ([], casts) = lock $
    do podcastlist_raw <- getSelectedPodcasts (gdbh gi) casts
       let podcastlist = filter_disabled podcastlist_raw
       episodelist <- mapM (getEpisodes (gdbh gi)) podcastlist
       let episodes = filter (\.x -> epstatus x == Pending) . concat $ episodelist
       i $ printf "%d episode(s) to consider from %d podcast(s)"
         (length episodes) (length podcastlist)
       downloadEpisodes gi episodes
       cleanupDirectory gi episodes

cleanupDirectory gi episodes =
    do base <- getEnclTmp
       files <- getDirectoryContents base
       mapM_ (removeold base) files
    where epmd5s = map (getdlfname . epurl) episodes
          epmsgs = map (\e -> e ++ ".msg") epmd5s
          eps = epmd5s ++ epmsgs
          removeold base file =
            when ((not (file `elem` eps)) &&
                 (not (file `elem` [".", ".."]))) $
                removeFile (base ++ "/" ++ file)

downloadEpisodes gi episodes =
    do progressinterval <- getProgressInterval

       watchFiles <- newMVar []
       wfthread <- forkIO (watchTheFiles progressinterval watchFiles)

       easyDownloads "download" getEnclTmp True
                     (\pt -> mapM (ep2dlentry pt) episodes)
                     (procStart watchFiles)
                     (callback watchFiles)

    where nameofep e = printf "%d.%d" (castid . podcast $ e) (epid e)
          ep2dlentry pt episode =
              do cpt <- newProgress (nameofep episode)
                        (eplength episode)
                 addParent cpt pt
                 return $ DownloadEntry {dlurl = epurl episode,
                                         usertok = episode,
                                         dlname = nameofep episode,
                                         dlprogress = cpt}
          procStart watchFilesMV pt meter dlentry dltok =
              do writeMeterString stdout meter $
                  "Get: " ++ nameofep (usertok dlentry) ++ " "
                   ++ (take 60 . eptitle . usertok $ dlentry) ++ "\n"
                 modifyMVar_ watchFilesMV $ \wf ->
                     return $ (dltok, dlprogress dlentry) : wf

          callback watchFilesMV pt meter dlentry dltok status result =
              modifyMVar_ watchFilesMV $ \wf ->
                  do size <- checkDownloadSize dltok
                     setP (dlprogress dlentry) (case size of
                                                  Nothing -> 0
                                                  Just x -> toInteger x)
                     procEpisode gi meter dltok 
                                     (usertok dlentry) (dlname dlentry)
                                     (result, status)
                     return $ filter (\(x, _) -> x /= dltok) wf

-- FIXME: this never terminates, but at present, that may not hurt anything

watchTheFiles progressinterval watchFilesMV = 
    do withMVar watchFilesMV $ \wf -> mapM_ examineFile wf
       threadDelay (progressinterval * 1000000)
       watchTheFiles progressinterval watchFilesMV

    where examineFile (dltok, cpt) =
              do size <- checkDownloadSize dltok
                 setP cpt (case size of
                             Nothing -> 0
                             Just x -> toInteger x)

procEpisode gi meter dltok ep name r =
       case r of
         (Success, _) -> procSuccess gi ep (tokpath dltok)
         (Failure, Terminated sigINT) -> 
             do i "Ctrl-C hit; aborting!"
                -- Do not consider Ctrl-C a trackable error
                exitFailure
         _ -> do curtime <- now
                 let newep = considerDisable gi $
                       updateAttempt curtime $
                       (ep {eplastattempt = Just curtime,
                            epfailedattempts = epfailedattempts ep + 1})
                 updateEpisode (gdbh gi) newep
                 commit (gdbh gi)
                 writeMeterString stderr meter $ " *** " ++ name ++ 
                                      ": Error downloading\n"
                 when (epstatus newep == Error) $
                    writeMeterString stderr meter $ " *** " ++ name ++ 
                             ": Disabled due to errors.\n"
considerDisable gi ep = forceEither $
    do faildays <- get (gcp gi) cast "epfaildays"
       failattempts <- get (gcp gi) cast "epfailattempts"
       let lupdate = case epfirstattempt ep of
                        Nothing -> 0
                        Just x -> x
       let timepermitsdel = case eplastattempt ep of
                                Nothing -> True
                                Just x -> x - lupdate > faildays * 60 * 60 * 24
       case epstatus ep of
         Pending -> return $ ep {epstatus =
            if (epfailedattempts ep > failattempts) && timepermitsdel
                then Error
                else Pending}
         _ -> return ep 
                        
    where cast = show . castid . podcast $ ep
                  
updateAttempt curtime ep =
    ep {epfirstattempt =
        case epfirstattempt ep of
            Nothing -> Just curtime
            Just x -> Just x
       }


procSuccess gi ep tmpfp =
    do cp <- getCP ep idstr fnpart
       let cfg = get cp idstr
       let newfn = (strip $ forceEither $ cfg "downloaddir") ++ "/" ++
                   (strip $ forceEither $ cfg "namingpatt")
       createDirectoryIfMissing True (fst . splitFileName $ newfn)
       let renameTypes = getRenameTypes 
       
       realType <- (mkEnviron ep tmpfp) >>= (getRealType ep)
       let newep = ep {eptype = realType}
       finalfn <- case lookup (eptype newep) renameTypes of
                    Nothing -> movefile tmpfp newfn
                    Just suffix -> 
                        if not (isSuffixOf suffix newfn)
                           then movefile tmpfp (newfn ++ suffix)
                           else movefile tmpfp newfn

       environ <- mkEnviron newep finalfn
       let postProcTypes = fromJust $ getList (gcp gi) idstr "postproctypes"
       let postProcCommand = forceEither $ get (gcp gi) idstr "postproccommand" >>=
                          (return . strip)
       
       when (postProcCommand /= "" &&
             (postProcTypes == ["ALL"] ||
             (eptype newep) `elem` postProcTypes)) $
            do let postProcCommand = forceEither $ get (gcp gi) idstr "postproccommand"
               d $ "   Running postprocess command " ++ postProcCommand
               runSimpleCmd environ postProcCommand

       cp <- getCP newep idstr fnpart
       let cfg = get cp (show . castid . podcast $ newep)
       forM_ (either (const Nothing) Just $ cfg "posthook")
             (runHook finalfn)
       curtime <- now
       updateEpisode (gdbh gi) $ 
           updateAttempt curtime $ (newep {epstatus = Downloaded})
       commit (gdbh gi)
       
    where idstr = show . castid . podcast $ ep
          runSimpleCmd environ cmd =
              do ph <- runProcess "/bin/sh" ["-c", cmd] Nothing (Just environ)
                       Nothing Nothing Nothing
                 ec <- waitForProcess ph
                 d $ "  command exited with: " ++ show ec

          fnpart = snd . splitFileName $ epurl ep
          -- Given an episode and an environment, call the external
          -- command that determines the MIME type of that episode.
          -- If the command returns the empty string or exits with
          -- an error, just return (eptype ep) back to the caller.
          getRealType ep environ =
              do let typecmd = forceEither $ get (gcp gi) idstr "gettypecommand"
                 d $ "  Running gettypecommand " ++ typecmd
                 d $ "  Enrivonment for this command is " ++ show environ
                 (stdinh, stdouth, stderrh, ph) <-
                     runInteractiveProcess "/bin/sh" ["-c", typecmd]
                         Nothing (Just environ)
                 hClose stdinh
                 forkIO $ do c <- hGetContents stderrh
                             hPutStr stderr c

                 c <- hGetLine stdouth
                 hClose stdouth
                 ec <- waitForProcess ph
                 d $ "  gettypecommand exited with: " ++ show ec
                 d $ "  gettypecommand sent to stdout: " ++ show c
                 d $ "  original type was: " ++ show (eptype ep)
                 case ec of
                   ExitSuccess -> case (strip c) of
                                    "" -> return (eptype ep)
                                    x -> return x
                   _ -> return (eptype ep)

          getRenameTypes =
              case getList (gcp gi) idstr "renametypes" of
                Just x -> map procpair (map (span (/= ':')) x)
                Nothing -> []
          procpair (t, []) = (t, [])
          procpair (t, ':':x) = (t, x)
          procpair (t, x) = error $ "Invalid pair in renametypes: " ++ 
                            show (t, x)
          
          mkEnviron ep fn =
              do oldenviron <- getEnvironment
                 return $ newenviron ++ oldenviron
              where newenviron =
                        [("CASTID", show . castid . podcast $ ep),
                         ("CASTTITLE", castname . podcast $ ep),
                         ("EPFILENAME", fn),
                         ("EPURL", epurl ep),
                         ("FEEDURL", feedurl . podcast $ ep),
                         ("SAFECASTTITLE", sanitize_fn . castname . podcast $ ep),
                         ("SAFEEPTITLE", sanitize_fn . eptitle $ ep),
                         ("EPTITLE", eptitle ep)]

-- | Runs a hook script.
runHook :: String -- ^ The name of the file to pass as an argument to the script.
        -> String -- ^ The name of the script to invoke.
        -> IO ()
runHook fn script =
    do child <- forkProcess runScript
       status <- getProcessStatus True False child
       case status of
         Nothing -> fail "No status unexpected."
         Just (Stopped _) -> fail "Stopped process unexpected."
         Just (Terminated sig) -> fail (printf "Post-hook \"%s\" terminated by signal %s" script (show sig))
         Just (Exited (ExitFailure code)) -> fail (printf "Post-hook \"%s\" failed with exit code %s" script (show code))
         Just (Exited ExitSuccess) -> return ()
    where runScript =
              -- Open /dev/null, duplicate it to stdout, and close it.
              do bracket (openFd "/dev/null" ReadOnly
                                 Nothing defaultFileFlags)
                         closeFd
                         (\devNull ->
                              do dupTo devNull stdOutput)
                 executeFile script False [fn] Nothing

getCP :: Episode -> String -> String -> IO ConfigParser
getCP ep idstr fnpart =
    do cp <- loadCP
       return $ forceEither $
              do cp <- if has_section cp idstr
                          then return cp
                          else add_section cp idstr
                 cp <- set cp idstr "safecasttitle" 
                       (sanitize_fn . castname . podcast $ ep)
                 cp <- set cp idstr "epid" (show . epid $ ep)
                 cp <- set cp idstr "castid" idstr
                 cp <- set cp idstr "safefilename" 
                       (sanitize_fn (unEscapeString fnpart))
                 cp <- set cp idstr "safeeptitle" (sanitize_fn . eptitle $ ep)
                 return cp

movefile old new =
    do realnew <- findNonExisting new
       copyFile old (realnew ++ ".partial")
       renameFile (realnew ++ ".partial") realnew
       removeFile old
       return realnew

findNonExisting template =
    do dfe <- doesFileExist template
       if (not dfe)
          then return template
          else do let (dirname, fn) = splitFileName template
                  (fp, h) <- openTempFile dirname fn
                  hClose h
                  return fp

"""
