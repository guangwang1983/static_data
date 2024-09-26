

for closeprice in $(ls close_price*)
do
    echo $closeprice
    tail -n 30 $closeprice | awk -F "," '{sum+=$2;c++}END{sum/=c;print sum}'
done
