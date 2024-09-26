#!/bin/sh
if [ $# -eq 0 ]; then
	echo "\$1 = sleep in sec before script starts."
	echo "\$2 = TXMerger name."
	exit	
fi

sleep $1
basedir=$(pwd)
#temp_alldatesfile_path=$(mktemp /tmp/dates.XXXXXX)
temp_alldatesfile_path=$basedir/temp_alldatesfile.dat
#cp $STATICDATAPATH/datesfiles/DYNAMIC_DATESFILE_SIMDATES $temp_alldatesfile_path
cp testdates $temp_alldatesfile_path

echo "# tx merge"
rm TM_SL*/tx.h5*
start_all_txh5_background.sh $temp_alldatesfile_path $2

sleep 10
background_run_check.sh $2
sleep 3

start_all_pnlgen_background.sh
sleep 3
background_run_check.sh pnl_condor
sleep 3
rm condor_args*
