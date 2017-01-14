#!/usr/bin/env python

from __future__  import print_function
import errno
import os
import sys
import shutil
import datetime
import time
import collections

def recollindex_running(pid_file_path):
    try:
        pid_file = open(pid_file_path)
    except IOError as e:
        if e.errno == 2:
            sys.stderr.write("Error: Could not find 'index.pid' at {}\n".format(pid_file_path))
        else:
            sys.stderr.write("Error: Could not open 'index.pid' at {}\n".format(pid_file_path))
        raise

    recoll_pid_string = pid_file.read()
    if recoll_pid_string == '':
        return False

    try:
        recoll_pid = int(recoll_pid_string)
    except ValueError:
        sys.stderr.write("Error: Not a valid process ID: {}\n".format(recoll_pid_string))
        raise

    try:
        os.kill(recoll_pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            sys.stderr.write("Warning: {} has process ID {}, but no process with that ID is running.\n".format(pid_file_path, recoll_pid_string))
            return False
        else:
            raise

    return True

def latest_query(history_path):
    now = datetime.datetime.now()
    if os.path.isfile(history_path):
        history_timestamp = os.path.getmtime(history_path)
        date_last_query = datetime.datetime.fromtimestamp(history_timestamp)
    else:
        return None, now

    return date_last_query, now

def running_time(flintlock_path):
    if os.path.isfile(flintlock_path):
        flintflock_timestamp = os.path.getmtime(flintlock_path)
        now = datetime.datetime.now()
        date_recollindex_started = datetime.datetime.fromtimestamp(flintflock_timestamp)
    return date_recollindex_started, now

def since_last_run(idxstatus_path):
    if os.path.isfile(idxstatus_path):
        idxstatus_timestamp = os.path.getmtime(idxstatus_path)
        now = datetime.datetime.now()
        date_recollindex_last_started = datetime.datetime.fromtimestamp(idxstatus_timestamp)
    return date_recollindex_last_started, now

def parse_idxstatus(idxstatus_path, write_tempfiles=True):

    idxstatus = collections.OrderedDict()

    with open(idxstatus_path) as idxstatus_fp:
        text = idxstatus_fp.read()
    text_wrapped = text.replace('\\\n', '')
    for line in text_wrapped.splitlines():
        try:
            key, val = (x.strip() for x in line.split('=', 1))
        except ValueError:
            sys.stderr.write("Error: cannot parse line: {}\n".format(line))
            if write_tempfiles:
                import tempfile
                temp = tempfile.NamedTemporaryFile(prefix="idxstatus", delete=False)
                sys.stderr.write("Copying {} to {}\n".format(idxstatus_path, temp.name))
                idxstatus_fp.seek(0)
                temp.file.write(idxstatus_fp.read())
                temp.close()
            raise

        idxstatus[key] = val

    return idxstatus

def print_idxstatus(idxstatus):
    DbIxStatus = {
        '0' : "DBIXS_NONE",
        '1' : "DBIXS_FILES",
        '2' : "DBIXS_PURGE",
        '3' : "DBIXS_STEMDB",
        '4' : "DBIXS_CLOSING",
        '5' : "DBIXS_MONITOR",
        '6' : "DBIXS_DONE",
    }
    # https://bitbucket.org/medoc/recoll/src/dabc5bae1dd7f8b5049ef021c441ffb8050cd7eb/src/index/indexer.h?at=default&fileviewer=file-view-default#indexer.h-40
    try:
        print('DbIxStatus is', DbIxStatus[idxstatus['phase']])
        print('Files indexed:', idxstatus['docsdone'])
        print('Files checked:', idxstatus['filesdone'])
        print('Starting number of files:', idxstatus['dbtotdocs'])
        if idxstatus['phase'] == '1':
            print('Indexing this file or directory:', idxstatus['fn'])
        else:
            print('Not indexing files now.')
    except IndexError:
        pass

if __name__ == '__main__':

    if os.name != 'posix':
        sys.stderr.write("Error: unsupported OS: {}\n".format(os.name))
        # No standard way to check if a process is running, unfortunately.
        sys.exit(1)

    try:
        if shutil.which("recoll") is None:
            sys.stderr.write("Warning: could not find 'recoll' executable. Is recoll installed?\n")
    except AttributeError:
        # shutil.which() is only in python 3.3 and later.
        pass

    recoll_dir = os.path.expanduser("~/.recoll")
    if not os.path.isdir(recoll_dir):
        sys.stderr.write("Error: could not find 'recoll' directory here: {}\n".format(recoll_dir))
        sys.exit(1)

    if recollindex_running(os.path.join(recoll_dir, "index.pid")):
        print("recollindex is running")
        recollindex_start, then = running_time(os.path.join(recoll_dir, "xapiandb", "flintlock"))
        recollindex_elapsed_time = then - recollindex_start
        print(" recollindex has been running for {}".format(recollindex_elapsed_time))
        print_idxstatus(parse_idxstatus(os.path.join(recoll_dir, "idxstatus.txt")))
    else:
        print("recollindex is not running")
        recollindex_last_started, then = since_last_run(os.path.join(recoll_dir, "idxstatus.txt"))
        time_since_last_index = then - recollindex_last_started
        print(" recollindex was last started on {}".format(recollindex_last_started.ctime()))
        print(" time since recollindex last started: {}".format(time_since_last_index))

    date_of_last_query, date_now = latest_query(os.path.join(recoll_dir, "history"))
    if date_of_last_query:
        duration_since_last_query = date_now - date_of_last_query

        print("recoll database last queried on: {}".format(date_of_last_query.ctime()))
        print(" which was {} ago.".format(duration_since_last_query))
