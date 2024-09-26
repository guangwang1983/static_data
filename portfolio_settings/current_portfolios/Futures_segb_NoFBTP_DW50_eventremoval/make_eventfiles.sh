file=$1

while read LINE
do
    name=$(echo $LINE | awk '{printf "%s",$1}')
    echo $LINE > ${name}_event.dat
done < $file
