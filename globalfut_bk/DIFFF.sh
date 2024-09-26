diff -y MULTIPORTFOLIO_ACCUM_OOS_DEBUGCurve/DailyResult.out SINGLEPORTFOLIO_ACCUM_OOS_DEBUGCurve/DailyResult.out | grep "|" | sed 's/;/ /g' | awk '{if(($2-$5)*($2-$5)>1){print $1" "$2-$5}}'
