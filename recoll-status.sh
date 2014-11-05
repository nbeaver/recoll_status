#!/usr/bin/env bash

set -eu

function print_duration {
	local total_seconds="$@"
	local s_per_m=60
	local s_per_h=$(($s_per_m * 60))
	local s_per_d=$(($s_per_h * 24))
	local days=$(($total_seconds / $s_per_d))
	local hours=$(($total_seconds / $s_per_h))
	local minutes=$(($total_seconds / $s_per_m))
	local seconds=$(($total_seconds - $s_per_m*$minutes - $s_per_h*$hours - $s_per_d*$days))
	printf "$days days $hours hours $minutes minutes\n"
}

function status_running {
	echo 'recollindex is running.'
	local date_start=$(date +%c --reference ~/.recoll/xapiandb/flintlock)
	local secs_start=$(date +%s --reference ~/.recoll/xapiandb/flintlock)
	local secs_now=$(date +%s)
	local secs_since_start=$(($secs_now - $secs_start))
	printf 'recollindex has been running for '
	print_duration "$secs_since_start"
}

function status_not_running {
	echo 'recollindex is not running.'
	local date_last_index=$(date +%c --reference ~/.recoll/idxstatus.txt)
	local secs_last_index=$(date +%s --reference ~/.recoll/idxstatus.txt)
	local secs_now=$(date +%s)
	local secs_since_last_index=$(($secs_now - $secs_last_index))
	echo "recollindex was last run on $date_last_index"
	printf "duration since last run: "
	print_duration "$secs_since_last_index"
}

if [ -s ~/.recoll/index.pid ]
then
	status_running
else
	status_not_running
fi

# TODO: recollindex has been running for # minutes.
# TODO: recollindex has indexed #/# files (#%)
# TODO: check that recoll is installed and there is a ~/.recoll folder.
# TODO: check when it was last opened.
