#!/bin/sh
TIMESTAMP=$(date -d today "+%Y%m%d")
cd $PRODUCTIONPORTFOLIOPATH
multiportfolios_update_wq.py --releasedate $TIMESTAMP --multiportfoliopath $PRODUCTIONPORTFOLIOPATH/${1}
