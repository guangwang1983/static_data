
#STRATEGY;TYPE;ID;TARGET;BASESYM;POOL;REMOVE;CORRMAX;MAXIND;STARTTIME;ENDTIME;CORRELATION;TSTIME;TETIME
#STRATEGY;LEG1;LEG2;LEG3;STARTTIME;ENDTIME;TARGETCORR;INDICATORCORR;TSTIME;TETIME
#stime=13
#etime=14
basedir=$(pwd)
while read LINE
do
    stime=$(echo $LINE | awk -F ";" '{print $9}')
    etime=$(echo $LINE | awk -F ";" '{print $10}')
    target=$(echo $LINE | awk -F ";" '{print $2}')
    modelid=$(echo $LINE | awk -F ";" '{print $3"_"$4}')
    dir=$(ls -d TM_SL3L_${target}_${modelid}*)
    echo $dir
    echo $stime" "$etime
    cd $dir
    if [ "$stime" == "09:00:00" ]; then
        plotModelPnl_wq.py --modelstr B  --sdate 2015-01-01 --etime 14:00:00 --edate $1 > allresults1400_${1}.dat&
    else
        plotModelPnl_wq.py --modelstr B --sdate 2015-01-01 --stime $stime --etime 14:00:00 --edate $1 > allresults1400_${1}.dat&
    fi
    cd $basedir

done < models.cfg_noheader

