SEGDIRS=$(ls -d SEGMENT*)
basedir=$(pwd)
for seg in $SEGDIRS
do
    echo $seg
    cd $basedir/$seg
    globdirs=$(ls -d GLOBAL*)
    for globdir in $globdirs
    do
        echo $globdir
        cd $basedir/$seg/$globdir
        rm optconfigweights_flat.dat
        for w in $(ls S*_weights.dat) 
        do
            cat $w >> optconfigweights_flat.dat
        done
        
    done


done
