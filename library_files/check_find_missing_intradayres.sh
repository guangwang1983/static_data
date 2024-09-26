sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    for modeldir in $(ls -d TM_*)
    do
        nofiles=$(ls -l $modeldir/basesignals/B*/IntradayResults.h5 | wc -l)
        noconfigs=$(ls -d $modeldir/basesignals/B* | wc -l)
        if [ ${nofiles} != ${noconfigs} ]; then 
            echo $modeldir
            echo $nofiles/$noconfigs
            for b in $(ls -d $modeldir/basesignals/B*)
            do
                size=$(ls -l $basedir/$sublib/$b/IntradayResults.h5 | awk '{printf "%s",$5}')
                if [ $size == "0" ]; then
                    ls -d $basedir/$sublib/$b
                fi
            done
        fi
    done
    #

    cd $basedir
done
