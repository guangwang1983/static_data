dirs=$(cat $1)

for d in $dirs
do
    mkdir $d
    cp -r /dat/matterhorn/production/library/$d/settings $d/
    cp -r /dat/matterhorn/production/library/$d/models.cfg $d/
    cp -r /dat/matterhorn/production/library/$d/slrlmodels.cfg $d/
done
