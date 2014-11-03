#!/usr/bin/env bash

if [ -s ~/.recoll/index.pid ]
then
	echo 'recollindex is running.'
else
	echo 'recollindex is not running.'
fi
