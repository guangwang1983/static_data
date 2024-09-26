DIRS=$(ls -d TM_*)
basedir=$(pwd)
for dir in $DIRS
do
    cd $dir
    convert2EOD_seq.py --stime 12:30:00 --etime 21:30:00&
    cd $basedir
done
