#!/bin/sh
TIMESTAMP=$(date -d today "+%Y%m%d")
cd /dat/matterhorn/production/portfolios/productionportfolio_FX_MultiBook
multiportfolios_update_wq.py --releasedate $TIMESTAMP --multiportfoliopath /dat/matterhorn/production/portfolios/productionportfolio_FX_MultiBook/${1}
