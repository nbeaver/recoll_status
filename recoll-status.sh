#!/usr/bin/env bash

if [ -s ~/.recoll/index.pid ]
then
	echo 'recollindex is running.'
else
	echo 'recollindex is not running.'
fi

# TODO: recollindex has been running for...
# TODO: recollindex has indexed #/# files (#%)
# TODO: check that recoll is installed and there is a ~/.recoll folder.
# TODO: check when it was last opened.
