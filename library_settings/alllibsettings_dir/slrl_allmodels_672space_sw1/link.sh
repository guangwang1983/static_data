

for model in $(cat /dat/matterhorn10/production/library/slrl_allmodels_672space/succesful_models1)
do
    ln -s /dat/matterhorn10/production/library/slrl_allmodels_672space/$model .
done
