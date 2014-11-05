#!/usr/bin/env bash

set -eu

function print_duration {
	local total_seconds="$@"
	local s_per_m=60
	local s_per_h=$(($s_per_m * 60))
	local s_per_d=$(($s_per_h * 24))
	local seconds_left=$total_seconds
	local days=$(($seconds_left / $s_per_d))
	local seconds_left=$(($seconds_left - $s_per_d*$days))
	local hours=$(($seconds_left / $s_per_h))
	local seconds_left=$(($seconds_left - $s_per_h*$hours))
	local minutes=$(($seconds_left / $s_per_m))
	local seconds_left=$(($seconds_left - $s_per_m*$minutes))
	printf "$days days $hours hours $minutes minutes $seconds_left seconds"
}

function status_query {
	local date_last_query=$(date +%c --reference ~/.recoll/history)
	local secs_last_query=$(date +%s --reference ~/.recoll/history)
	local secs_now=$(date +%s)
	local secs_since_last_query=$(($secs_now - $secs_last_query))
	echo "recoll was last queried on $date_last_query"
	printf " which was "
	print_duration "$secs_since_last_query"
	printf " ago.\n"
}

function status_running {
	echo 'recollindex is running.'
	local date_start=$(date +%c --reference ~/.recoll/xapiandb/flintlock)
	local secs_start=$(date +%s --reference ~/.recoll/xapiandb/flintlock)
	local secs_now=$(date +%s)
	local secs_since_start=$(($secs_now - $secs_start))
	printf ' recollindex has been running for '
	print_duration "$secs_since_start"
	printf '\n'
}

function status_not_running {
	echo 'recollindex is not running.'
	local date_last_index=$(date +%c --reference ~/.recoll/idxstatus.txt)
	local secs_last_index=$(date +%s --reference ~/.recoll/idxstatus.txt)
	local secs_now=$(date +%s)
	local secs_since_last_index=$(($secs_now - $secs_last_index))
	echo " recollindex was last started on $date_last_index"
	printf " duration since last run: "
	print_duration "$secs_since_last_index"
	printf '\n'
}

status_running
status_not_running

if [ ! $(type recoll) ]
then
	echo 'Command `recoll` not found. Is recoll installed?'
	exit 1
fi

if [ ! -d ~/.recoll ]
then
	echo 'No ~/.recoll direcotry. Is recoll installed?'
	exit 1
fi

if [ -s ~/.recoll/index.pid ]
then
	status_running
else
	status_not_running
fi

status_query

# DONE: recollindex has been running for # minutes.
# TODO: recollindex has indexed #/# files (#%)
# DONE: check that recoll is installed and there is a ~/.recoll folder.
# DONE: check when it was last queried
