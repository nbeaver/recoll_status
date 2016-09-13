#!/usr/bin/env python

import errno
import os
import sys

def recoll_running(recoll_dir):
    try:
        pid_file_path = os.path.join(recoll_dir, "index.pid")
        pid_file = open(pid_file_path)
    except IOError:
        sys.stderr.write("Could not find index.pid file: {}\n".format(pid_file_path))
        raise

    recoll_pid_string = pid_file.read()
    if recoll_pid_string == '':
        return False

    try:
        recoll_pid = int(recoll_pid_string)
    except ValueError:
        sys.stderr.write("Not a valid process ID: {}\n".format(recoll_pid_string))
        raise

    try:
        os.kill(recoll_pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            sys.stderr.write("Warning: recollindex process ID is {}, but no process with that ID is running.\n".format(recoll_pid_string))
            return False
        else:
            raise

    return True

if __name__ == '__main__':
    if os.name != 'posix':
        sys.stderr.write("Error: unsupported OS: {}\n".format(os.name))

    check_dir = os.path.expanduser("~/.recoll")
    recoll_running(check_dir)
