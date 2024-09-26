sublibs=$(cat $1)
basedir=$(pwd)

for sublib in $sublibs
do
    echo $sublib
    cd $sublib
    ls -l TM_*/basesignals/B*/IntradayResults.h5 | sed 's/://g' | sort -gk8 
    cd $basedir
done
