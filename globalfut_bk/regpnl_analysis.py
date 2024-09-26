import tables
from slrlmodel_multiday_libupdate_yearly_continuous import get_last_basesignal_cfg
import os
import griddata_util_continues
import ko_util


f=tables.open_file("eodResultSeg080000_140000.h5")
arr=f.get_node("/B10.C9").read()
date2pnl={line[2]:line[1] for line in arr}

#os.system("tar -xzf "+basesignal_dirname+"/basesignals"+current_date[0:4]+".h5"+".tar.gz")
basesignal_path = os.getcwd()
basesignalslrl_cfg_lines = open(basesignal_path+"/basesignalslrl.cfg",'r').readlines()

for line in basesignalslrl_cfg_lines:
    arr=line.strip().split()
    if arr[0] == "Modelline":
        all_kosyms=[x for x in griddata_util_continues.getAllProductNames(getfx="False") if x!=""]
        slrldict=ko_util.parse_slrl_cfg_line_sw(arr[1],all_kosyms)
    if arr[0] == "BaseSignal":
        basesignaldict={x.split(":")[0]:x.split(":")[1] for x in arr[1:]}
        basesignaldict["BaseSignal_line"]=line.strip()

basesignalH5File=tables.open_file("basesignals2023.h5")
mainbasesignaldict = basesignaldict
for key in date2pnl:
    if "2023" in key:
        print key+" : "+str(date2pnl[key])+" -> "+get_last_basesignal_cfg(key.replace("-",""),mainbasesignaldict,basesignalH5File)["RegressionCorrelation"]


