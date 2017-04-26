.. -*- coding: utf-8 -*-

=========================================
Script to check status of ``recollindex``
=========================================

:Author: Nathaniel Beaver
:Copyright: This document has been placed in the public domain.

The GUI for `Recoll`_ reports indexing progress that looks like this::

    Indexing in progress: Updating (42252 docs/38419 files/2166 errors/38419 tot files)

However, there is no convenient `command to report its status`_ during indexing.
The files in ``~/.recoll/`` have a lot of information about the status of the database and the ``recollindex`` process,
though it is somewhat inconvenient to interpret this information.
To make it easier,
this repository provides a python script to give information about how long it's been since the last index,
if a ``recollindex`` process is running and, if so,
what it is doing and how far along it is.

.. _Recoll: http://www.lesbonscomptes.com/recoll/
.. _command to report its status: https://bitbucket.org/medoc/recoll/issue/154/show-status-of-how-many-documents-are-not

Here is an example of the output::

    $ recollstatus.py
    recollindex is running
     recollindex has been running for 0 days, 0:06:08.344198
    DbIxStatus is DBIXS_FILES
    Files indexed: 2000
    Files checked: 133226
    Starting number of files: 227407
    Indexing this file or directory: /usr/share/doc/wordplay/copyright
    recoll database last queried on: Tue Sep 13 12:43:48 2016
     which was 0 days, 10:28:48.988676 ago.

----------------------
Heuristics for output.
----------------------

- If ``~/.recoll/index.pid`` is not an empty file, then recollindex is running.
  This process id can be used for looking up the process as well.
  Its modification time is the time when recollindex started or stopped running.
- The file ``~/.recoll/idxstatus.txt`` shows the progress and current file.
  Its modification time is the last successful update of ``recollindex``.
  (This may not be the current time if ``recollindex`` gets stuck.)

  Values in ``idxstatus``:

  ``phase`` == ``DbIxStatus``::
  
      0 = DBIXS_NONE
      1 = DBIXS_FILES
      2 = DBIXS_PURGE
      3 = DBIXS_STEMDB
      4 = DBIXS_CLOSING
      5 = DBIXS_MONITOR
      6 = DBIXS_DONE

  ``docsdone`` = Documents actually updated

  ``filesdone`` = Files tested (updated or not)

  ``dbtotdocs`` = Doc count in index at start

  ``totfiles`` = Total files in index.

  https://bitbucket.org/medoc/recoll/src/3b851ca464ae9a7698c16e448d8c1caac1b9b646/src/index/indexer.h

- The file ``~/.recoll/xapiandb/flintlock`` seems to be always empty.
  Its modification time is the time when ``recollindex`` started running.
- The file ``~/.recoll/history`` gives the query history.
  Its modification date is the last time a query was run with ``recoll -t`` or the graphical recoll closed.

Thus:

- To find the time when indexing started, look at ``flintlock``
- To find the time when indexing was halted, look at ``index.pid`` (unless it's an empty file).
- To find the time when indexing last successfully indexed a file, look at ``idxstatus.txt``.
- To find the time when indexing succesfully completed -- impossible?
- To find the time when a query last ran, look at ``history``.

-------
License
-------

This project is licensed under the terms of the `MIT license`_.

.. _MIT license: LICENSE.txt
