#!/usr/bin/env python

import errno
import os
import sys
import shutil

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

if __name__ == '__main__':

    if os.name != 'posix':
        sys.stderr.write("Error: unsupported OS: {}\n".format(os.name))
        # No standard way to check if a process is running, unfortunately.
        sys.exit(1)

    try:
        if shutil.which("recoll") is None:
            sys.stderr.write("Warning: could not find 'recoll' executable. Is recoll installed?\n")
    except AttributeError:
        pass

    recoll_dir = os.path.expanduser("~/.recoll")
    if not os.path.isdir(recoll_dir):
        sys.stderr.write("Error: could not find 'recoll' directory here: {}\n".format(recoll_dir))
        sys.exit(1)

    if recollindex_running(recoll_dir):
        sys.stdout.write("recollindex is running\n")
    else:
        sys.stdout.write("recollindex is not running\n")
