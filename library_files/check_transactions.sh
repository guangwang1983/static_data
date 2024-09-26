sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    for modeldir in $(ls -d TM_*)
    do
        echo $modeldir
        ls -l $modeldir/configs/B*/tradesignals2022.h5 | sort -gk5r | tail
        nofiles=$(ls -l $modeldir/configs/B*/tradesignals2022.h5 | wc -l)
        noconfigs=$(ls -d $modeldir/configs/B* | wc -l)
        echo $nofiles/$noconfigs
    done
    #

    cd $basedir
done
