## What PyHpodder does

PyHpodder is a podcast aggregator.  For each user it has a database to keep track of the podcasts to which they are subscribed.  By default, when running the **pypod** executable program, feeds of the subscribed podcasts are read and new episodes are noted in the database; then the new episodes are downloaded.

## Why the project is useful

PyHpodder is a work-alike program to replace [hpodder](https://github.com/jgoerzen/hpodder).  hpodder once was supplied by Debian and related Linux distros.  When hpodder became unsupported and was removed from Debian, I wrote PyHpodder to download the podcast episodes from my hpodder subscriptions.  The database and configuration files are compatible with hpodder.

**pypod** is intended to be run from the command line making it work well when run periodically via a crontab entry.

PyHpodder is a small body of code, yet writing it served as a way to master the python language.

## How users can get started with the project

Clone this project into a local directory.  Then it can be run via the command:
```
PyHpodder/bin/pypod
```

At present, there is no installer for PyHpodder.  On Debian-like distros, you can manually install PyHpodder for use by all users via these commands:
```
sudo cp PyHpodder/bin/* /usr/local/bin/
sudo cp -r PyHpodder/pypod /usr/local/
```

## Where users can get help with your project

Since at present there is no PyHpodder man page, one should start by reading the [hpodder documentation](https://github.com/jgoerzen/hpodder/wiki).

pypod provides online help.  Here is the output showing the commands that have been implemented.
```
$ pypod -h
Usage: pypod [global-options] <command> [command-options]
 Run "pypod lscommands" for a list of available commands.
 Run "pypod <command> -h" for help on a particular command.
 Run "pypod -h" for available global-options.

Options:
  -?, -h, --help  Show this help message and exit.
  -d, --debug     Enable debugging printouts.

$ pypod lscommands
All available commands:
 Name        Description
----------  -------------------------------------------------------------
add         Add new podcasts
catchup     Ignore older undownloaded episodes
disable     Stop updating and downloading given podcasts
download    Downloads pending podcast episodes (run update first)
enable      Enable podcasts that were previously disabled
fetch       Scan feeds, then download new episodes
lscasts     List subscribed podcasts
lscommands  Display a list of all available commands
lsepisodes  List episodes in the database
rm          Remove podcast(s) from the database
setstatus   Modify the status of selected episodes
settitle    Modify the stored title of a podcast
update      Scan feeds and update list of available downloads
```

## Who maintains and contributes to the project

I am the only maintainer.  I am not seeking other developers, but I will consider contributions.  Because I actively use pypod on a daily basis, there is some ongoing maintenance.

## How does pypod work?

For each user, PyHpodder stores private files in `~/.hpodder/`.  Downloaded episodes are stored in `~/podcasts/` or a subdirectory of `~/podcasts/`.

The file `~/.hpodder/hpodder.conf` contains the user's preferences, where one can select directory and filename for downloaded episodes.  One also can specify a command to execute for each downloaded episode.

The file `~/.hpodder/hpodder.db` is the database that tracks podcasts and episodes.

## Copyright

PyHpodder is derived from hpodder.  PyHpodder licensed under GPLv3.

##  Future work being considered

- Fix failing ssl downloads.  This will probably entail moving to python3 and using the [Requests library](http://docs.python-requests.org) to download feeds and episodes.
- Add documentation, at least a manpage.
- Add a command to import subscriptions from an OPML file.
- Add a command to export subscriptions to an OPML file.
- Package this software for Debian and possibly for Fedora.  Thus providing installers for the related Linux distros.
- Implement missing hpodder features (e.g. multiple concurrent downloads).
- Adding features that are incompatable with hpodder, such as storing episode descriptions in the database.  To avoid breaking hpodder, this would include moving the private files to a different sub-directory.


