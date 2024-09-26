#!/bin/sh
basedir=$(pwd)
#temp_alldatesfile_path=$(mktemp /tmp/dates.XXXXXX)
temp_alldatesfile_path=$basedir/temp_alldatesfile.dat
cp $STATICDATAPATH/datesfiles/DYNAMIC_DATESFILE_SIMDATES $temp_alldatesfile_path

#temp_weeklydatesfile_path=$(mktemp /tmp/dates_weekly_update.XXXXXX)
temp_weeklydatesfile_path=$basedir/temp_weeklydatesfile.dat
cat dates  > $temp_weeklydatesfile_path
echo "Dates to be run:"
cat  $temp_weeklydatesfile_path

rm *pnl_error.out
rm -r jobmanager_stderr*
rm -r ko_condor.results

sleep 7200

# transaction gen
simulation_manager_wq.py --datesfile $temp_weeklydatesfile_path --simulationtype tradesignal --restart True

# transaction gen
simulation_manager_wq.py --datesfile $temp_weeklydatesfile_path --simulationtype execution --restart True

# tx merge
rm TM*/tx.h5
start_all_txh5_background.sh $temp_alldatesfile_path IR5_TXMerger

sleep 30
background_run_check.sh IR5_TXMerger
sleep 600
start_all_pnlgen_background.sh
sleep 30
background_run_check.sh pnl_condor_l
sleep 30
rm condor_args*
rm -r ko_condor.results
