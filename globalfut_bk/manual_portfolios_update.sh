#!/bin/sh
TIMESTAMP=$1
reduce_machines.sh
start_nodes10.sh
sleep 100

#STATIC GM & CURVE
cd $PRODUCTIONPORTFOLIOPATH
productionportfolios_update_wq.py --releasedate $TIMESTAMP
#SPOT FX
cd $PRODUCTIONPORTFOLIOFXPATH
multiportfolios_update_wq.py --releasedate $TIMESTAMP --multiportfoliopath $PRODUCTIONPORTFOLIOFXPATH/GLOBAL_LIVE_PRODUCTION_PORTFOLIO

sleep 300
stop_nodes10.sh
