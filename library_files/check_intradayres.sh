sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    nointraday=$(ls -l TM_*/basesignals/B*/IntradayResults.h5 | wc -l)
    nobasesignals=$(ls -d TM_*/basesignals/B* | wc -l)
    echo $nointraday/$nobasesignals
    ls -l TM_*/basesignals/B*/IntradayResults.h5
    #

    cd $basedir
done
