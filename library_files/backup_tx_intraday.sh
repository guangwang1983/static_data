sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    models=$(ls -d TM_*)
    for m in $models
    do
        pwd
        echo cd $basedir/$sublib/$m/basesignals
        cd $basedir/$sublib/$m/basesignals
        basesignals=$(ls -d B*)
        for b in $basesignals
        do
            cp $basedir/$sublib/$m/basesignals/$b/IntradayResults.h5.backup.20230707 $basedir/$sublib/$m/basesignals/$b/IntradayResults.h5
#            rm $basedir/$sublib/$m/basesignals/$b/IntradayResults.h5.backup.20230303
#            cp $basedir/$sublib/$m/basesignals/$b/IntradayResults.h5 $basedir/$sublib/$m/basesignals/$b/IntradayResults.h5.backup.20230707
        done
    done

    cd $basedir
done
