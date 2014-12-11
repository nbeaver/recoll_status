.. -*- coding: utf-8 -*-

====================================
Script to check status of ``recoll``
====================================

:Author: Nathaniel Beaver
:Copyright: This document has been placed in the public domain.

`Recoll`_ currently provides no convenient `command to report its status`_ during indexing.
However, the files in ``~/.recoll/`` have a lot of information about the status of the database,
though it is somewhat inconvenient to interpret this information.
To make this easier,
this repository has a combination shell/python script to give information about how long it's been since the last index,
if a ``recollindex`` process is running and, if so,
what it is doing and how far a long it is.

.. _Recoll: http://www.lesbonscomptes.com/recoll/
.. _command to report its status: https://bitbucket.org/medoc/recoll/issue/154/show-status-of-how-many-documents-are-not

- If ``~/.recoll/index.pid`` is not an empty file, then recollindex is running.
  This process id can be used for looking up the process as well.
  Its modification time is the time when recollindex started or stopped running.
- The file ``~/.recoll/idxstatus.txt`` shows the progress and current file.
  It be used to compute percent completion.
  Its modification time is the last successful update of ``recollindex``.
  (This may not be the current time if ``recollindex`` gets stuck.)

  Values in ``idxstatus``:

  ``phase`` == ``DblxStatus``::
  
      0 = DBIXS_NONE
      1 = DBIXS_FILES
      2 = DBIXS_PURGE
      3 = DBIXS_STEMDB
      4 = DBIXS_CLOSING
      5 = DBIXS_MONITOR
      6 = DBIXS_DONE

  http://fossies.org/dox/recoll-1.19.14/classDbIxStatus.html#ab4c35685f98ff539b71c21784f7c2951

  ``docsdone`` = Documents actually updated

  ``filesdone`` = Files tested (updated or not)

  ``dbtotdocs`` = Doc count in index at start

  http://fossies.org/dox/recoll-1.19.14/indexer_8h_source.html

- The file ``~/.recoll/xapiandb/flintlock`` seems to be always empty.
  Its modification time is the time when ``recollindex`` started running.
- The file ``~/.recoll/history`` gives the query history.
  Its modification date is the last time a query was run with ``recoll -t`` or the graphical recoll closed.

Thus:

- To find the time when indexing started, look at ``flintlock``
- To find the time when indexing was halted, look at ``index.pid``.
- To find the time when indexing last successfully indexed a file, look at ``idxstatus.txt``.
- To find the time when indexing succesfully completed -- impossible?
- To find the time when a query last ran, look at ``history``.
