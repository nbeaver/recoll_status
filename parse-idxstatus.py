#!/usr/bin/env python
import os

DblxStatus = {
'0' : "DBIXS_NONE",
'1' : "DBIXS_FILES",
'2' : "DBIXS_PURGE",
'3' : "DBIXS_STEMDB",
'4' : "DBIXS_CLOSING",
'5' : "DBIXS_MONITOR",
'6' : "DBIXS_DONE",
}

idxstatus_path = os.path.expanduser('~/.recoll/idxstatus.txt')

with open(idxstatus_path) as db_status:
    for line in db_status:
        key, val = (x.strip() for x in line.split('='))
        if key == 'phase':
            print 'DblxStatus is',DblxStatus[val]
            status = val
        elif key == 'docsdone':
            print 'Files indexed:',val
            files_indexed = int(val)
        elif key == 'filesdone':
            print 'Files checked:',val
            files_checked = int(val)
        elif key == 'dbtotdocs':
            print 'Starting number of files:',val
            num_initial_files = int(val)
        elif key == 'fn':
            if status == '1':
                print 'Indexing this file or directory:', val
            else:
                print 'Not indexing files now.'
