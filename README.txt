Recoll currently has no way to report its status.
However, the files in ~/.recoll/ have a lot of information about the status of the database.

-- If ~/.recoll/index.pid is not an empty file, then recollindex is running.
   This process id can be used for looking up the process as well.
   Its modification time is the time when recollindex started running.
-- The file ~/.recoll/idxstatus.txt shows the progress and current file.
   It be used to compute percent completion.
   Its modification time is the last successful update of recollindex.
   (This may not be the current time if recollindex gets stuck.)
-- The file ~/.recoll/xapiandb/flintlock seems to be always empty.
   Its modification time is the time when recollindex started running.
-- The file ~/.recoll/history gives the query history.
   Its modification date is the last time a query was run with recoll -t or the graphical recoll closed.

Thus:
To find the time when indexing started, look at flintlock or index.pid.
To find the time when indexing last successfully indexed a file, look at idxstatus.txt.
To find the time when indexing succesfully completed -- ?
To find the time when a query last ran, look at history.
