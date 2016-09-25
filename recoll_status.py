#!/usr/bin/env python

from __future__  import print_function
import errno
import os
import sys
import shutil
import datetime
import time

def recollindex_running(pid_file_path):
    try:
        pid_file = open(pid_file_path)
    except IOError:
        sys.stderr.write("Error: Could not find 'index.pid' at {}\n".format(pid_file_path))
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
    if os.path.isfile(history_path):
        history_timestamp = os.path.getmtime(history_path)
        now = datetime.datetime.now()
        date_last_query = datetime.datetime.fromtimestamp(history_timestamp)
    else:
        sys.stderr.write("Error: Could not find 'history' at {}\n".format(history_path))
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

def print_idxstatus(idxstatus_path):
    if not os.path.isfile(idxstatus_path):
        return None
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
    idxstatus = open(idxstatus_path, 'rb')
    for line_bytes in idxstatus.readlines():
        line = line_bytes.decode()
        try:
            key, val = (x.strip() for x in line.split('=', 1))
        except ValueError:
            sys.stderr.write("Error: cannot parse line: {}\n".format(line))
            import tempfile
            temp = tempfile.NamedTemporaryFile(prefix="idxstatus", delete=False)
            sys.stderr.write("Copying {} to {}\n".format(idxstatus_path, temp.name))
            idxstatus.seek(0)
            temp.file.write(idxstatus.read())
            temp.close()
            break

        if key == 'phase':
            print('DbIxStatus is', DbIxStatus [val])
            status = val
        elif key == 'docsdone':
            print('Files indexed:',val)
            files_indexed = int(val)
        elif key == 'filesdone':
            print('Files checked:',val)
            files_checked = int(val)
        elif key == 'dbtotdocs':
            print('Starting number of files:',val)
            num_initial_files = int(val)
        elif key == 'fn':
            if status == '1':
                print('Indexing this file or directory:', val)
            else:
                print('Not indexing files now.')

    idxstatus.close()

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
        print(" recollindex has been running for {} days, {}".format(recollindex_elapsed_time.days, recollindex_elapsed_time))
        print_idxstatus(os.path.join(recoll_dir, "idxstatus.txt"))
    else:
        print("recollindex is not running")
        recollindex_last_started, then = since_last_run(os.path.join(recoll_dir, "idxstatus.txt"))
        time_since_last_index = then - recollindex_last_started
        print(" recollindex was last started on {}".format(recollindex_last_started.ctime()))
        print(" time since recollindex last started: {} days, {}".format(time_since_last_index.days, time_since_last_index))

    date_of_last_query, date_now = latest_query(os.path.join(recoll_dir, "history"))
    if date_of_last_query is None:
        sys.exit(1)
    duration_since_last_query = date_now - date_of_last_query

    print("recoll database last queried on: {}".format(date_of_last_query.ctime()))
    print(" which was {} days, {} ago.".format(duration_since_last_query.days, duration_since_last_query))
