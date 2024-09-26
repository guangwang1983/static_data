#!/bin/bash
set -e
figures=$(cat $1)

function calc()
{
for fig in $figures
do
    impact_avg=$(cat ko_ecocalendar_201* | grep $fig | awk -F ";" 'BEGIN{sum=0;}{sum+=$7;c++;}END{if(c>0){sum/=c;print sum}else{print 0}}')
    COMPARE=$(echo "scale=10; ($impact_avg >= 2)" | bc -l | xargs printf "%1.0f")
    if [ $COMPARE -gt 0 ];then
    	echo "1 "$fig" "$impact_avg
    else
    	echo "0 "$fig" "$impact_avg
    fi	
done
}

#calc 

calc | sort -nk1 | awk '{if($1==1){print $2" "$3" --> ADD FIGURE!"}else{print $2" "$3}}'
