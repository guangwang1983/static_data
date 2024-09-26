if [ $# -ne 2 ]; then
	echo "Usage <old str> <new str>"
	exit
fi

DIRS=$(ls -d *$1*)
OLD=$1
NEW=$2

for dir in $DIRS
do
	newdir=$( echo $dir | sed "s/^${1}/${2}/g")
	mv $dir $newdir
done

