sublibs=$(cat slrl.dat)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    models=$(ls -d TM_*)
    for m in $models
    do
        rm $m/basesignals/B*/tx.h5
        rm $m/basesignals/B*/IntradayResults.h5
        #rm $m/basesignals/B*/overnightstats.cfg
        #rm $m/basesignals/B*/basesignalhist/*h5*
        #rm $m/basesignals/B*/overnightstatshist/*h5*
        #rm $m/configs/B*/tradesignals20*.h5&
        #rm $m/configs/B*/transactions20*.h5
    done

    cd $basedir
done
