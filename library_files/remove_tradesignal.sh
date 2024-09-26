sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    models=$(ls -d TM_*)
    for m in $models
    do
        rm $m/configs/B*/tradesignals2021.h5
        rm $m/configs/B*/tradesignals2020.h5
        rm $m/configs/B*/tradesignals201*.h5
    done

    cd $basedir
done
