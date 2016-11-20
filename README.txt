README.txt for Pyhpodder

NOTE:	config.py sets the application data directory to ~/.hpodder_dev
	This needs to be corrected before release.

NOTE: Instead of carrying enum within our sources, on Debian, require python-enum.  Python 3.4 will include this enum package in the standard library.


Tree:
=====
.:
bin  hpodder  README.txt

./bin:
pypod

./hpodder:
commands  __init__.py  lib  main.py

./hpodder/commands:
add.py      download.py        fetch.py     ls.py  set_status.py  setup.py
catchup.py  enable_disable.py  __init__.py  rm.py  set_title.py   update.py

./hpodder/lib:
config.py  db.py  enum.py  __init__.py  ppod_types.py  url_getter.py  utils.py


Dependencies among my files:
============================
bin/pypod:		hpodder/__init__.py  hpodder/main.py
hpodder/__init__.py:	(none)
hpodder/main.py:	commands/__init__.py  lib/config.py  lib/db.py  lib/utils.py
commands/add.py:	lib/db.py  lib/ppod_types.py
commands/catchup.py:	lib/db.py  lib/ppod_types.py  lib/utils.py
commands/download.py:	lib/config.py  lib/db.py  lib/ppod_types.py  lib/url_getter.py  lib/utils.py
commands/enable_disable.py:  lib/db.py  lib/ppod_types.py  lib/utils.py
commands/fetch.py:	lib/config.py  lib/utils.py
commands/__init__.py:	commands/[a-z]*.py  lib/utils.py
commands/ls.py:		lib/db.py  lib/utils.py
commands/rm.py:		lib/db.py  lib/utils.py
commands/set_status.py:	lib/db.py  lib/ppod_types.py  lib/utils.py
commands/set_title.py:	lib/db.py  lib/utils.py
commands/setup.py:	lib/config.py  lib/utils.py
commands/update.py:	lib/config.py  lib/db.py  lib/ppod_types.py  lib/url_getter.py  lib/utils.py
lib/config.py:		(none)
lib/db.py:		lib/config.py  lib/ppod_types.py  lib/utils.py
lib/enum.py:		(none)
lib/__init__.py:	(none)
lib/ppod_types.py:	lib/enum.py
lib/url_getter.py:	lib/config.py  lib/utils.py
lib/utils.py:		lib/config.py


