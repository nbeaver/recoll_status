#!/usr/bin/env python

import errno
import os
import sys
import shutil
import datetime
import time

def recollindex_running(recoll_dir):
    try:
        pid_file_path = os.path.join(recoll_dir, "index.pid")
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

def latest_query(recoll_dir, outfile):
    history_path = os.path.join(recoll_dir, "history")
    if os.path.isfile(history_path):
        history_timestamp = os.path.getmtime(history_path)
        now = datetime.datetime.now()
        last_query = datetime.datetime.fromtimestamp(history_timestamp)
        duration_since_last_query = now - last_query
    else:
        sys.stderr.write("Error: Could not find 'history' at {}\n".format(history_path))
        return None

    outfile.write("recoll was last queried on {}\n".format(last_query.ctime()))
    outfile.write(" which was {} days, {} ago.\n".format(duration_since_last_query.days, duration_since_last_query))
    return last_query

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

    if recollindex_running(recoll_dir):
        sys.stdout.write("recollindex is running\n")
    else:
        sys.stdout.write("recollindex is not running\n")

    if latest_query(recoll_dir, sys.stdout) is None:
        sys.exit(1)
