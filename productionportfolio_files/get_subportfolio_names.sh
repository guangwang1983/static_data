

DIRS=$(cat $1)

for d in $DIRS
do
    cat /dat/matterhorn/production/portfolios/generate/$d/arguments.dat | awk '{print $11}'

done
