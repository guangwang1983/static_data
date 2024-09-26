
#STRATEGY;TYPE;ID;TARGET;BASESYM;POOL;REMOVE;CORRMAX;MAXIND;STARTTIME;ENDTIME;CORRELATION;TSTIME;TETIME
#stime=13
#etime=14
basedir=$(pwd)
while read LINE
do
    stime=$(echo $LINE | awk -F ";" '{print $13}')
    etime=$(echo $LINE | awk -F ";" '{print $14}')
    target=$(echo $LINE | awk -F ";" '{print $4}'| awk -F "." '{print $2"."$3}')
    modelid=$(echo $LINE | awk -F ";" '{print $3}')
    cd TM_SLRL_${target}_${modelid}
    echo TM_SLRL_${target}_${modelid}
    if [ "$stime" == "09:00:00" ]; then
        #echo plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime
        #plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime > allresults.dat&
        #plotModelPnl_wq.py --modelstr B  --etime $etime --spreadweight 1.0 --sdate 2020-08-01 > 202008allresults.dat_sw1&
        #plotModelPnl_wq.py --modelstr B  --etime $etime --spreadweight 3.0 --sdate 2020-08-01 > 202008allresults.dat_sw3&
        plotModelPnl_wq.py --modelstr B  --etime $etime --spreadweight 1.0  --edate $1 > allresults${1}.dat_sw1&
        plotModelPnl_wq.py --modelstr B  --etime $etime --spreadweight 3.0  --edate $1 > allresults${1}.dat_sw3&
    else
        #plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime --spreadweight 1.0 --sdate 2020-08-01 > 202008allresults.dat_sw1&
        #plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime --spreadweight 3.0 --sdate 2020-08-01 > 202008allresults.dat_sw3&
        plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime --spreadweight 1.0  --edate $1 > allresults${1}.dat_sw1&
        plotModelPnl_wq.py --modelstr B --stime $stime --etime $etime --spreadweight 3.0  --edate $1 > allresults${1}.dat_sw3&
    fi
    cd $basedir

done < slrlmodels.cfg_noheader

