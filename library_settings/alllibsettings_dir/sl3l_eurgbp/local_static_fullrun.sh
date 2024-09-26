#!/bin/sh
if [ $# -eq 0 ]; then
    echo "\$1 = datesfile"
    echo "\$2 = TXMerger name"
    exit
fi

BASEDIR=$(pwd)
#datesfiles.py --datesfile $1 
echo "-------------------------------"
datesfiles=$(ls $BASEDIR/datesfiles/dates20*)
for dfile in $datesfiles
do
    echo $dfile
    #simulation_manager_wq.py --datesfile $dfile --simulationtype tradesignal --restart True
    sleep 5
done

for dfile in $datesfiles
do
    simulation_manager_wq.py --datesfile $dfile --simulationtype execution --restart True
    sleep 5
    #Remove all signal h5 files for dfile year
    dfilename=$(echo $dfile | awk -F "/datesfiles/" '{printf "%s",$2}')
    year=$(echo $dfilename | tr -dc '0-9')
    if [ "$year" != "2020" ]; then
        for model in $(ls -d TM_*)
        do
            echo $model
            #rm ${model}/configs/B*/tradesignals$year.h5
        done
    fi
done

temp_alldatesfile_path=$BASEDIR/temp_alldatesfile.dat
cp $STATICDATAPATH/datesfiles/DYNAMIC_DATESFILE_SIMDATES $temp_alldatesfile_path

echo "# tx merge"
rm TM_*/tx.h5*
start_all_txh5_background.sh $temp_alldatesfile_path $2
sleep 30
background_run_check.sh $2
sleep 3
start_all_pnlgen_background.sh
