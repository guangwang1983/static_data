cat ko_ecocalendar_20160101_20161001.csv | grep "^USD" | grep "USD;3" | awk -F ";" '{if(substr($3,1,2)>14){a=substr($2,1,4);b=substr($2,5,2);c=substr($2,7,2);print a"-"b"-"c;}}'| sort |uniq
