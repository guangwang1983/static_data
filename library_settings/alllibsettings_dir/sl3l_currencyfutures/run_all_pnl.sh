#!/bin/sh
basedir=$(pwd)
temp_alldatesfile_path=$basedir/temp_alldatesfile.dat
cp $STATICDATAPATH/datesfiles/DYNAMIC_DATESFILE_SIMDATES $temp_alldatesfile_path

start_all_pnlgen_background.sh
sleep 30
background_run_check.sh pnl_condor
sleep 30
rm condor_args*
