#!/usr/bin/env python

from __future__ import print_function
import errno
import os
import shutil
import datetime
import collections
import argparse
import logging
import sys
logger = logging.getLogger(__name__)

def recollindex_running(pid_filepath):
    # Example PID file path: ~/.recoll/index.pid
    try:
        pid_file = open(pid_filepath)
    except IOError as e:
        if e.errno == 2:
            logger.error(
                "Could not find 'index.pid' at '{}'\n".format(pid_filepath))
        else:
            logger.error(
                "Could not open 'index.pid' at '{}'\n".format(pid_filepath))
        raise

    try :
        recoll_pid_string = pid_file.read()
    except Exception as e:
        logger.error(
            "Could not read 'index.pid' at '{}'\n".format(pid_filepath))
        raise

    logger.debug("recoll_pid_string = '{}'".format(recoll_pid_string))
    if recoll_pid_string == "":
        return False

    try:
        recoll_pid = int(recoll_pid_string)
    except ValueError:
        logger.error("Not a valid process ID: {}".format(recoll_pid_string))
        raise
    logger.info("recoll_pid = '{}'".format(recoll_pid))

    # TODO: split this into a separate function and handle things more cleanly.
    # https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python
    # https://stackoverflow.com/questions/7647167/check-if-a-process-is-running-using-python-on-linux
    # https://unix.stackexchange.com/questions/169898/what-does-kill-0-do
    try:
        os.kill(recoll_pid, 0)
    except OSError as e:
        logger.debug("e.errno = '{}'".format(e.errno))
        if e.errno == errno.ESRCH:
            logger.warning(
                "'{}' has process ID '{}', but no process with that ID is running.".
                format(pid_filepath, recoll_pid))
            return False
        elif e.errno == errno.EPERM:
            logger.warning(
                "'{}' has process ID '{}', but that process is running under a different user.".
                format(pid_filepath, recoll_pid))
            return True
        else:
            logger.error("sent signal to PID: '{}'".format(recoll_pid))
            raise

    return True


def latest_query(history_path):
    # Caveat: this is only valid if history is enabled.
    now = datetime.datetime.now()
    if os.path.isfile(history_path):
        history_timestamp = os.path.getmtime(history_path)
        date_last_query = datetime.datetime.fromtimestamp(history_timestamp)
    else:
        return None, now

    return date_last_query, now


def last_started(flintlock_path):
    flintflock_timestamp = os.path.getmtime(flintlock_path)
    now = datetime.datetime.now()
    date_recollindex_started = datetime.datetime.fromtimestamp(
        flintflock_timestamp)
    return date_recollindex_started, now


def since_last_started(flintlock_path):
    # Files that should also work:
    # ~/.recoll/index.pid
    timestamp = os.path.getmtime(flintlock_path)
    now = datetime.datetime.now()
    date_recollindex_last_started = datetime.datetime.fromtimestamp(timestamp)
    return date_recollindex_last_started, now


def since_last_active(idxstatus_path):
    if os.path.isfile(idxstatus_path):
        idxstatus_timestamp = os.path.getmtime(idxstatus_path)
        now = datetime.datetime.now()
        date_recollindex_last_active = datetime.datetime.fromtimestamp(
            idxstatus_timestamp)
    return date_recollindex_last_active, now


def write_tempfile(fp, prefix):
    import tempfile

    temp = tempfile.NamedTemporaryFile(prefix=prefix, delete=False)
    logger.info("Copying {} to {}\n".format(fp.name, temp.name))
    fp.seek(0)
    temp.file.write(fp.read())
    temp.close()


def write_tempfile_text(text, prefix):
    import tempfile

    temp = tempfile.NamedTemporaryFile(prefix=prefix, delete=False)
    logger.info("Copying to {}\n".format(temp.name))
    temp.file.write(text)
    temp.close()


def parse_idxstatus(idxstatus_fp, write_tempfiles=True):
    idxstatus = collections.OrderedDict()

    text = idxstatus_fp.read()
    if text == "":
        logger.warning("idxstatus file is blank")
        return idxstatus

    text_wrapped = text.replace("\\\n", "")
    for line in text_wrapped.splitlines():
        try:
            key, val = (x.strip() for x in line.split("=", 1))
        except ValueError:
            logger.error("Cannot parse line: {}\n".format(line))
            if write_tempfiles:
                # If the parsing the idxstatus file fails,
                # keep a copy of it for later debugging.
                write_tempfile(idxstatus_fp, prefix="idxstatus")
                write_tempfile_text(text, prefix="idxstatus_txt")
            raise

        idxstatus[key] = val

    if "phase" not in idxstatus:
        write_tempfile(idxstatus_fp, prefix="idxstatus")
        write_tempfile_text(text, prefix="idxstatus_txt")
        raise ValueError("No 'phase' field in file '{}'".format(
            idxstatus_fp.name))

    if idxstatus["phase"] in ["0", "5"]:
        # Don't have examples of these to test with yet.
        write_tempfile(idxstatus_fp, prefix="idxstatus")
        write_tempfile_text(text, prefix="idxstatus_txt")

    return idxstatus


def format_idxstatus(idxstatus):
    # TODO: should this even be included, since it can change with each version?
    DbIxStatus_before_v1p30p1 = {
        "0": "DBIXS_NONE",
        "1": "DBIXS_FILES",
        "2": "DBIXS_PURGE",
        "3": "DBIXS_STEMDB",
        "4": "DBIXS_CLOSING",
        "5": "DBIXS_MONITOR",
        "6": "DBIXS_DONE",
    }
    DbIxStatus = {
        "0": "DBIXS_NONE",
        "1": "DBIXS_FILES",
        "2": "DBIXS_FLUSH",
        "3": "DBIXS_PURGE",
        "4": "DBIXS_STEMDB",
        "5": "DBIXS_CLOSING",
        "6": "DBIXS_MONITOR",
        "7": "DBIXS_DONE",
    }
    try:
        phase_number = idxstatus["phase"]
        try:
            phase_name = DbIxStatus[phase_number]
            try:
                phase_name_old = DbIxStatus_before_v1p30p1[phase_number]
            except KeyError:
                phasen_name_old = None
            if phase_name == phase_name_old:
                formatted = [
                    "DbIxStatus is {} ({})".format(phase_number, phase_name)
                ]
            else:
                formatted = [
                    "DbIxStatus is {} ({} or {} for version 1.31.0 and earlier)".format(phase_number, phase_name, phase_name_old)
                ]
        except KeyError:
            formatted = [
                "DbIxStatus is {} (unknown phase)".format(phase_number)
            ]
    except KeyError:
        formatted = []
    # https://framagit.org/medoc92/recoll/-/blob/9d3869c2b954fb8e90cd7f0b1465fe358dbc49c3/src/index/idxstatus.h#L27
    descriptors = collections.OrderedDict()
    descriptors["docsdone"] = "Documents updated:                    "
    descriptors["filesdone"] = "Files tested:                         "
    descriptors["filerrors"] = "Failed files:                         "
    descriptors["totfiles"] = "Total files in index:                 "
    descriptors["dbtotdocs"] = "Starting number of indexed documents: "
    for field, description in descriptors.items():
        if field in idxstatus:
            formatted.append("{} {}".format(description, idxstatus[field]))
    if "phase" in idxstatus:
        if idxstatus["phase"] == "1":
            formatted.append("Indexing this file: {}".format(idxstatus["fn"]))
        else:
            formatted.append("Not indexing files now.")
    else:
        formatted.append("Indexing phase unknown (blank idxstatus file?)")

    return "\n".join(formatted)


def recollstatus(recoll_dir):
    status = []
    try :
        is_running = recollindex_running(os.path.join(recoll_dir, "index.pid"))
    except Exception as e :
        sys.stdout.error(e.message, e.args)
        is_running = None

    if is_running is None:
        status.append("not sure if recollindex is running or not")
    elif is_running:
        status.append("index.pid matches running process")
        recollindex_start, then = last_started(
            os.path.join(recoll_dir, "xapiandb", "flintlock"))
        recollindex_elapsed_time = then - recollindex_start
        status.append(" recollindex was last started on: {}".format(
            recollindex_start.ctime()))
        status.append(" recollindex has been running for: {}".format(
            recollindex_elapsed_time))
    else:
        status.append("index.pid does not match a running process")
        recollindex_start, then = last_started(
            os.path.join(recoll_dir, "xapiandb", "flintlock"))
        time_since_last_started = then - recollindex_start
        recollindex_last_active, then = since_last_active(
            os.path.join(recoll_dir, "idxstatus.txt"))
        time_since_last_index = then - recollindex_last_active
        status.append(" recollindex was last started on: {}".format(
            recollindex_start.ctime()))
        status.append(" recollindex was last active on:  {}".format(
            recollindex_last_active.ctime()))
        status.append(" time since recollindex last started: {}".format(
            time_since_last_started))
        status.append(" time since recollindex last active:  {}".format(
            time_since_last_index))

    idxstatus_path = os.path.join(recoll_dir, "idxstatus.txt")
    with open(idxstatus_path) as idxstatus_fp:
        status.append(format_idxstatus(parse_idxstatus(idxstatus_fp)))

    date_of_last_query, date_now = latest_query(
        os.path.join(recoll_dir, "history"))
    if date_of_last_query:
        duration_since_last_query = date_now - date_of_last_query

        status.append("recoll database last queried on: {}".format(
            date_of_last_query.ctime()))
        status.append(" which was {} ago.".format(duration_since_last_query))

    return "\n".join(status)


def readable_directory(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            "not an existing directory: {}".format(path))
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(
            "not a readable directory: {}".format(path))
    return path

def get_default_recoll_dir():
    """
    "This configuration is the one used for indexing and querying when no
    specific configuration is specified. It is located in ``$HOME/.recoll/``
    for **Unix**-like systems and ``%LOCALAPPDATA%\\Recoll`` on **Windows**
    (typically ``C:\\Users\\[me]\\Appdata\\Local\\Recoll``)."
    <https://www.lesbonscomptes.com/recoll/usermanual/usermanual.html>
    """
    try:
        HOME = os.environ['HOME']
        logger.debug("HOME = '{}'".format(HOME))
    except KeyError:
        HOME = None

    if HOME is not None:
        unix_path = os.path.join(HOME, '.recoll')
        logger.debug("looking for Unix path: '{}'".format(unix_path))
        if os.path.exists(unix_path):
            logger.debug("Unix path exists: '{}'".format(unix_path))
            return unix_path
        else:
            logger.debug("Unix path does not exist: '{}'".format(unix_path))

    try :
        LOCALAPPDATA = os.environ['LOCALAPPDATA']
        logger.debug("LOCALAPPDATA = '{}'".format(HOME))
    except KeyError:
        LOCALAPPDATA = None

    if LOCALAPPDATA is not None:
        windows_path = os.path.join(LOCALAPPDATA, 'Recoll')
        logger.debug("looking for Windows path: '{}'".format(windows_path))
        if os.path.exists(windows_path):
            logger.debug("Windows path exists: '{}'".format(windows_path))
            return windows_path
        else:
            logger.debug("Windows path does not exist: '{}'".format(windows_path))

    raise FileNotFoundError("Could not find recoll directory in default location.")


def main():
    parser = argparse.ArgumentParser(
        description="Display status of recollindex.")
    parser.add_argument(
        "-d",
        "--recoll-dir",
        type=readable_directory,
        default=None,
        help="Recoll directory",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="More verbose logging",
        dest="loglevel",
        default=logging.WARNING,
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-b",
        "--debug",
        help="Enable debugging logs",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    args = parser.parse_args()
    # Initialize to avoid this error:
    # "No handlers could be found for logger"
    logging.basicConfig()
    logger.setLevel(args.loglevel)

    # Need to do this after logger is set up.
    if args.recoll_dir is None:
        recoll_dir = get_default_recoll_dir()
    else:
        recoll_dir = args.recoll_dir

    try:
        if shutil.which("recoll") is None:
            logger.warning(
                "Could not find 'recoll' executable. Is recoll installed?\n")
    except AttributeError:
        # shutil.which() is only in python 3.3 and later.
        pass

    print(recollstatus(recoll_dir))

if __name__ == "__main__":
    main()
