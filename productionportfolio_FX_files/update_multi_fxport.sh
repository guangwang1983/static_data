#!/bin/sh
TIMESTAMP=$(date -d today "+%Y%m%d")
cd $PRODUCTIONPORTFOLIOFXPATH
multiportfolios_update_wq.py --releasedate $TIMESTAMP --multiportfoliopath $PRODUCTIONPORTFOLIOFXPATH/${1}
