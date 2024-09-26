
for PORTNUMBER in `seq 1 5`
do
    python ~/src/script/python/createPortfolioFridayPeriodsSizeBound.py --sublibfile sublib.dat --pwindow 200 --portfolios $PORTNUMBER --stime 14:00:00 --etime 21:00:00 --sdate 20150102 --edate 20160311 --grid 30Min --segment 1400_2100 --noprocesses 20 --cov 99 --sfb 0.1 --smb 1 --tfb 40 --gridbase 0 --squashparam 3,3 --driftfilter 600D,900D,1200D --weight_mul 20 --config_wbound 1 --model_wbound 10 --symbol_wbound 15 --expand True
   rm -r SEGMENT1400_2100_GLOBALPORTFOLIO$((PORTNUMBER+1)) 
done

