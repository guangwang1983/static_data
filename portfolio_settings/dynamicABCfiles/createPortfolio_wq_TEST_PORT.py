#!/dat/matterhorn/env27/bin/python
import os, sys, time, argparse, imp
#import collections
import dateutil.parser
from collections import defaultdict,OrderedDict
import pandas as pd
from pandas import Series, DataFrame
import datetime
import numpy as np
from pandas import read_csv
import glob
import csv
import math
import ko_util, ko_probutil, ko_portfolio_util
#from Kapomega import *
import ModelStats, PortFolioOptimization
import tables 
#from Kapomega import DataManager
from hdf5_data_manager import Hdf5DataManager as DataManager
from portfolio_functions_wq import *
from copy import deepcopy
from staticDataHandler import StaticDataHandler
import gc
from dateutil.relativedelta import relativedelta
from engineConfigParser import ConfigParamParser
import condor_util
import pickle

import multiprocessing

def parallel_local_run(NoProcesses, jobs_data):
    pool = multiprocessing.Pool(NoProcesses)
    #processdict=dict()
    output = pool.map(create_input, jobs_data)
    pool.terminate()
    pool.join()
    return output
#Standard np.datetime64 format (notice the T):
#"YYYY-mm-ddTHH:MM:SS"

def create_input((GLOBALPORTFOLIODIR,portenddate,modelportfolioname,input_dict)):
    #input_dict
    #portenddate
    ko_util.ensure_dir(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+portenddate.strftime('%Y%m%d')+"/")
    modelportfolionamepath=GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+portenddate.strftime('%Y%m%d')+"/"+modelportfolioname
    ko_util.ensure_dir(modelportfolionamepath+"/")
    #Save down inputs as pickle file.
    input_picklefile=modelportfolionamepath+"/input_picklefile.dat"
    wfile=open(input_picklefile,'wb')
    wfile.write(pickle.dumps([portenddate,input_dict]))
    wfile.close()
    return "done"



def main(argv=None):
    if argv is None:
        argv = sys.argv
	#echo "-portfoliosfile <filename> -updatefreq <update freq in days> -oosstart <First oos date> -pwindow <PORTFOLIO WINDOW> -portfolios <PORTFOLIONO> -datesfile <datesfile> -gpweights <COV/SHARPE>" 
    parser = argparse.ArgumentParser()
    parser.add_argument("--po_framework", help="po_framework: sw_layer, sw_single, sw_model.", required=True)
    parser.add_argument("--segment", help="segment name (str)", required=True)
    parser.add_argument("--sublibfile", help="sublib handling file", required=True)
    parser.add_argument("--pwindow", help="portfolio window", required=True)
    parser.add_argument("--portfolios", help="number of portfolios", required=True)
    parser.add_argument("--stime", help="start time: HH:MM:SS", required=True)
    parser.add_argument("--etime", help="end time: HH:MM:SS", required=True)
    parser.add_argument("--sdate", help="oos start date: YYYYMMDD", required=True)
    parser.add_argument("--edate", help="oos end date: YYYYMMDD", required=True)
    parser.add_argument("--grid", help="10Min,30Min,60Min,Daily,Dynamic", required=True)
    parser.add_argument("--sfb", help="selection fraction bound (0-1)", required=True)
    parser.add_argument("--smb", help="sharpe model bound (0-5)", required=True)
    parser.add_argument("--noprocesses", help="Number of processes (default 50)",default=50, required=False)
    parser.add_argument("--tfb", help="trade freq bound (0-1)",default=30, required=False)
    parser.add_argument("--gridbase", help="0 or 30", required=True)
    parser.add_argument("--squashparams", help="3,3 SM,PO",default="3,3", required=True)
    parser.add_argument("--weight_mul", help="weight multiplier",default="100", required=False)
    parser.add_argument("--config_wbound", help="config weight bound as fraction of simulated size",default="1", required=False)
    parser.add_argument("--model_wbound", help="model weight bound in percent of target rootsym",default="50", required=False)
    parser.add_argument("--expand", help="expand number of periods to existing portfolios",default=False, required=False)
    parser.add_argument("--eventfile", help="eventfile name", required=False, default="none")
    parser.add_argument("--removedaysfile", help="remove days", required=False, default="none")
    parser.add_argument("--condorgridjobsize", help="condor grid job size",default="100", required=False)
    parser.add_argument("--gridpause", help="pause (in sec) between gridjob submissions",default=10, required=False)    
    parser.add_argument("--overwrite_segmenttime", help="use modelportfolios.cfg trade time instead",default="False", required=False)    
    parser.add_argument("--globalopt", help="opt,sharpe,flat",default="opt", required=False)
    parser.add_argument("--smscheme", help="SlotManager Scheme dvloop,fullspace",default="dvloop", required=False)
    parser.add_argument("--strategyframework", help="SLRL,SLRD",default="SLRL", required=False)
    args = parser.parse_args(argv[1:])
    #args = parser.parse_args('')#argv[1:])
    BASEDIR=os.getcwd()
    #-------------------------------
    lweight_bounds=[float(args.config_wbound),float(args.model_wbound)]
    squashparams=[int(args.squashparams.strip().split(',')[0]),int(args.squashparams.strip().split(',')[1])]
    #driftarr=args.driftfilter.strip().split(',')
    smscheme_val = args.smscheme 
    selectfracbound = float(args.sfb)
    selectmodelbound = (float(args.smb),50) #Model Trade Frequency Bound HARDCODED to 50
    tradefreqbound = float(args.tfb)
    NoProcesses = int(args.noprocesses)
    subLibFileLines = open(args.sublibfile, 'r').readlines()
    NOPORTFOLIOS=int(args.portfolios)
    PORTFOLIOWINDOW=int(math.floor(int(args.pwindow)*1.45)) #Roughly converting calendar days to trading days#TODO
    SEGMENTNAME=args.segment
    RESULTGRID=args.grid
     
    #Event Removal list :
    #-------------------------------
    eventlist=[]
    if args.eventfile != "none":
        eventlist = [(line.strip().split()[0],line.strip().split()[1]) for line in open(args.eventfile).readlines()]
    remove_special_days=[]
    if args.removedaysfile != "none":
        remove_special_days = [line.strip() for line in open(args.removedaysfile).readlines()]
    #-------------------------------

    #Base Signal Filter:
    #-------------------------------
    basesignalfilterdict=ko_portfolio_util.get_basesignalfilter(BASEDIR)
    if os.path.exists(BASEDIR+"/baseSignalFilterSublib.cfg"):
        basesignalfilter_sublib_dict=ko_portfolio_util.get_basesignalfilter_sublib(BASEDIR)
    else:
        basesignalfilter_sublib_dict=dict()

    #-------------------------------

    #Start/End Date and Segment time:
    #-------------------------------
    RUN_OOS_STARTDATE=args.sdate
    RUN_OOS_ENDDATE=args.edate
    STARTTIMESTR=args.stime
    ENDTIMESTR=args.etime
    
    #-------------------------------
    SEGMENTGRIDNAME="seg_"+STARTTIMESTR.split(":")[0]+STARTTIMESTR.split(":")[1]+"_"+ENDTIMESTR.split(":")[0]+ENDTIMESTR.split(":")[1]
    #-------------------------------
    #Fix replacement issue
    RUN_OOS_STARTDATE = datetime.datetime.strptime(RUN_OOS_STARTDATE+" "+STARTTIMESTR, "%Y%m%d %H:%M:%S").date()
    RUN_OOS_ENDDATE = datetime.datetime.strptime(RUN_OOS_ENDDATE+" "+STARTTIMESTR, "%Y%m%d %H:%M:%S").date()
    #-------------------------------
    #Write down arguments:
    argumentsFile=open("arguments.dat","w")
    if "expand" in " ".join(argv):
        argumentsFile.write(" ".join(argv)+"\n")
    else:
        argumentsFile.write(" ".join(argv)+" --expand True\n")
    argumentsFile.close()  
    #-------------------------------
   
    #Create periods file: 
    #-------------------------------
    periodFile=open("periods.dat","w")
    base = RUN_OOS_STARTDATE
    step = datetime.timedelta(days=1)
    perioddate_list=[]
    cnt=0
    while base <= RUN_OOS_ENDDATE:
        if base.weekday() == 4:
            perioddate_list.append(base)
            #print str(cnt)+" : "+str(base)
            cnt+=1
        base+=step

    for period in xrange(len(perioddate_list)):
        #print str(period)
        PORTENDDATE=perioddate_list[period]
        #PORTENDDATE=RUN_OOS_STARTDATE + datetime.timedelta(days=ADDDAYS) 
        PORTSTARTDATE=PORTENDDATE - datetime.timedelta(days=PORTFOLIOWINDOW)
        OOSSTARTDATE=PORTENDDATE + datetime.timedelta(days=1)
        if period == (len(perioddate_list)-1): 
            OOSENDDATE=RUN_OOS_ENDDATE
        else:
            OOSENDDATE=perioddate_list[period+1]
        periodFile.write("Period "+str(period)+": "+str(PORTSTARTDATE)+" "+str(PORTENDDATE)+" "+str(OOSSTARTDATE)+" "+str(OOSENDDATE)+"\n")
    periodFile.close()    
    #-------------------------------

    #PORTFOLIO LOOP:
    if args.expand:
        perioddate_list_org = deepcopy(perioddate_list)
    #---------------------------------------------------------
    for GPNO in xrange(1,NOPORTFOLIOS+1,1):
        print "SEGMENT: "+SEGMENTNAME+" --> GLOBALPORTFOLIO "+str(GPNO)
        print "---------------------------------------------------------"
        if args.expand:
            perioddate_list=deepcopy(perioddate_list_org)
        GLOBALPORTFOLIODIR=BASEDIR+"/"+"SEGMENT"+SEGMENTNAME+"_GLOBALPORTFOLIO"+str(GPNO)
         
        #for idx,date in enumerate(perioddate_list):
        #    print str(idx)+", Run Date: "+date.strftime('%Y%m%d')+" :"
        
        #---------------------------------------------------------
        #SUBLIBRARY LOOP
        #---------------------------------------------------------
        for sublibdat_line in subLibFileLines:
            sublibdat_line=sublibdat_line.strip()
            sublibpath=sublibdat_line.split(" ")[0]
            sublibname=sublibdat_line.split(" ")[0].split('/')[-1]
            #/apps/levelup/production/library/
            CASE_sublibpath="/".join(sublibpath.split("/")[:-1])+"/CASELIB_"+sublibname
             
            MODELPORTFOLIOFILE=sublibdat_line.split(" ")[2]
            CLASSIFICATION_TYPE=sublibdat_line.split(" ")[3]
            smArgs=ko_util.readDict(os.environ["STATICDATAPATH"]+"/SlotManagerSettings/"+sublibdat_line.split()[1])
            #Change to SUBLIBRARY DIR for data loading:
            if CLASSIFICATION_TYPE == "FULLSPACE":
                smscheme_val = "fullspace" #Model Space
            if CLASSIFICATION_TYPE == "DVLOOP":
                smscheme_val = "dvloop" #Basesignal Space
            os.chdir(sublibpath)
            #Parameters for all basesignals under sublibrary
            basesignalparamdict=ko_portfolio_util.get_basesignal_params_dict(sublibname)
            #MODELPORTFOLIO LOOP! (Create, pair, triple, regr), #modelportfolio = portfolio of models each with a batch of configs
            #---------------------------------------------------------
            for modelporfolioline in open(BASEDIR+"/"+MODELPORTFOLIOFILE,'r').readlines()[1:]:
                print str(modelporfolioline)
                if modelporfolioline.strip() == "":
                    print "empty line in modelporfolio file."
                    continue

                #------------------------
                modelportfolioname = ko_portfolio_util.getModelPortfolioName(modelporfolioline)
                modelporfolio=ko_portfolio_util.getmodelnames(modelporfolioline)
                strategy_type=ko_portfolio_util.getStrategyType(modelporfolioline)
                print "modelporfolio: "
                print modelporfolio
                print "Strategy Type: "+strategy_type
                #------------------------
                
                leg_rootsyms = ko_portfolio_util.getAllLegRootSyms(modelporfolioline)
                (trade_starttime,trade_endtime) = ko_portfolio_util.getStartEndTimeSegVol(modelporfolioline)
                mindrift,maxdrift = ko_portfolio_util.getMinMaxDrift(modelporfolioline)
                
                rootsym_fee_dict=dict()
                for rootsym in leg_rootsyms:
                    rootsym_fee_dict[rootsym]=(StaticDataHandler(rootsym)).getTradingFee()
                    print rootsym+" -2xfee: "+str(-2.0*rootsym_fee_dict[rootsym])
                print "trade_starttime,trade_endtime: "+trade_starttime+","+trade_endtime
                print "=================================================" 
                print "GLOBALPORTFOLIO: "+str(GPNO)+", "+sublibname
                print "=================================================" 
                print "Get configs for :"+modelportfolioname
               
                MAXWINDOW=max(1.45*int(smArgs['SW']),PORTFOLIOWINDOW)
                RUN_IS_STARTDATE=RUN_OOS_STARTDATE - datetime.timedelta(days=MAXWINDOW)
                USE_STARTTIMESTR=STARTTIMESTR
                USE_ENDTIMESTR=ENDTIMESTR
                tstime_sec=int(trade_starttime.split(":")[0])*3600 + int(trade_starttime.split(":")[1])*60 + int(trade_starttime.split(":")[2])
                segstime_sec=int(STARTTIMESTR.split(":")[0])*3600 + int(STARTTIMESTR.split(":")[1])*60 + int(STARTTIMESTR.split(":")[2])
                tetime_sec=int(trade_endtime.split(":")[0])*3600 + int(trade_endtime.split(":")[1])*60 + int(trade_endtime.split(":")[2])
                segetime_sec=int(ENDTIMESTR.split(":")[0])*3600 + int(ENDTIMESTR.split(":")[1])*60 + int(ENDTIMESTR.split(":")[2])
                if args.overwrite_segmenttime == "True":
                    if tstime_sec > segstime_sec:
                        USE_STARTTIMESTR=trade_starttime
                    if tetime_sec < segetime_sec:
                        USE_ENDTIMESTR=trade_endtime

                print "Starttime: "+USE_STARTTIMESTR
                print "Endtime: "+USE_ENDTIMESTR
                
                os.chdir(BASEDIR) #print os.getcwd()
                
                input_dict=dict()
                input_dict={"smscheme":smscheme_val,"strategy_type":strategy_type,"remove_special_days":remove_special_days,"po_framework":args.po_framework,"basesignalfilter_sublib_dict":basesignalfilter_sublib_dict,"basesignalfilterdict":basesignalfilterdict,"ENDTIMESTR":ENDTIMESTR,"STARTTIMESTR":STARTTIMESTR,"maxdrift":maxdrift,"mindrift":mindrift,"gridbase":args.gridbase,"RESULTGRID":RESULTGRID,"eventlist":eventlist,"RUN_OOS_ENDDATE":RUN_OOS_ENDDATE,"RUN_IS_STARTDATE":RUN_IS_STARTDATE,"USE_STARTTIMESTR":USE_STARTTIMESTR,"USE_ENDTIMESTR":USE_ENDTIMESTR,"GLOBALPORTFOLIODIR":GLOBALPORTFOLIODIR,"GPNO":GPNO,"BASEDIR":BASEDIR,"SEGMENTNAME":SEGMENTNAME,"sublibpath":sublibpath,"sublibname":sublibname,"modelporfolio":modelporfolio,"smArgs":smArgs,"modelportfolioname":modelportfolioname,"PORTFOLIOWINDOW":PORTFOLIOWINDOW, "selectfracbound":selectfracbound,"selectmodelbound":selectmodelbound,"tradefreqbound":tradefreqbound,"squashparams":squashparams,"WEIGHT_MUL":int(args.weight_mul),"lbounds":lweight_bounds,"classification_type":CLASSIFICATION_TYPE,"basesignalparamdict":basesignalparamdict} 
                
                #Create job for each period/modelportfolio in parallel: 
                #jobsdata=[]
                #for portenddate in perioddate_list:
                #    jobsdata.append([GLOBALPORTFOLIODIR,portenddate,modelportfolioname,input_dict])
                #para_output = parallel_local_run(NoProcesses,jobsdata)
                    
                
        #===================================================================
        #READ INPUT and create grid_joblist    
        #===================================================================
        modelportfolio_period_calculation_script="modelportfolio_period_calculation_slrl.py"
        if args.strategyframework == "SLRD":
            modelportfolio_period_calculation_script="modelportfolio_period_calculation_slrd.py"
        grid_joblist=[]
        sequential_joblist=[]    
        for portenddate in perioddate_list:
            modelportfolionamepath_list=glob.glob(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+portenddate.strftime('%Y%m%d')+"/MODELPORTFOLIO*")
            for modelportfolionamepath in modelportfolionamepath_list:
                newlist=["/dat/matterhorn/env27/bin/python",os.environ["SCRIPTPATH"]+"/python/"+modelportfolio_period_calculation_script,modelportfolionamepath+"/input_picklefile.dat",modelportfolionamepath+"/result_picklefile.dat"]
                sequential_joblist.append(newlist)
                if len(sequential_joblist)>10:
                    grid_joblist.append(sequential_joblist)
                    sequential_joblist=[]
        if len(sequential_joblist)>0:
            grid_joblist.append(sequential_joblist)
        
        #===================================================================
        #condor_util.launch_gridjobs(grid_joblist,args.condorgridjobsize,args.gridpause)
        #===================================================================

        #===================================================================
        #READ RESULTS: and create global portfolio: 
        #===================================================================
        MODELCONFIG_WEIGHTS=dict()
        MODELDATA=dict()
       
        for portenddate in perioddate_list:
            modelportfolionamepath_list=glob.glob(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+portenddate.strftime('%Y%m%d')+"/MODELPORTFOLIO*")
            for modelportfolionamepath in modelportfolionamepath_list:
                #read in results from all period/modelportfolio jobs:
                res=open(modelportfolionamepath+"/result_picklefile.dat","rb")
                dictData,dictWeights=pickle.load(res)
                if len(dictData)>0:
                    MODELDATA.update(dictData)
                    MODELCONFIG_WEIGHTS.update(dictWeights)
        #===================================================================
        print "#RESULT DATA:"
        print "------------------------------------------"
        dfMODELDATA=pd.DataFrame(MODELDATA)
        for key in dfMODELDATA:
           print key
        print "------------------------------------------"
        
        for period in xrange(0,len(perioddate_list),1):
            print "Period "+str(period)+": start portfolio weight calc:"
            print "Portfolio "+str(GPNO)+":"
            print "------------------------------------------------------------"    
            PORTENDDATE=perioddate_list[period]
            PORTSTARTDATE=PORTENDDATE - datetime.timedelta(days=PORTFOLIOWINDOW)
            OOSSTARTDATE=PORTENDDATE + datetime.timedelta(days=1) 
            #=========================================================================
            NotEmpty=True
            if PORTENDDATE.strftime('%Y%m%d') in dfMODELDATA.columns:
                rowno,colno = dfMODELDATA[PORTENDDATE.strftime('%Y%m%d')].shape
                print PORTENDDATE.strftime('%Y%m%d')+" : rows,cols: "+str(rowno)+","+str(colno)
                MSTATS=ModelStats.ModelStats(dfMODELDATA[PORTENDDATE.strftime('%Y%m%d')],PORTSTARTDATE,PORTENDDATE)
                shmodelweights=MSTATS.getdictValueWeights(MSTATS.getdictSharpe(dfMODELDATA[PORTENDDATE.strftime('%Y%m%d')].columns.values))
                meanmodelweights=MSTATS.getdictValueWeights(MSTATS.getdictMean(dfMODELDATA[PORTENDDATE.strftime('%Y%m%d')].columns.values))
                mean_adjusted_sharpeweights={key: shmodelweights[key]/meanmodelweights[key] for key,val in shmodelweights.iteritems()}
                
                #Normalize
                weightsum=np.sum(np.array(mean_adjusted_sharpeweights.values()),dtype=np.float64)
                mean_adjusted_sharpeweights={key: val/weightsum for key,val in mean_adjusted_sharpeweights.iteritems()}
                
                PO2=PortFolioOptimization.PortFolioOptimization(dfMODELDATA[PORTENDDATE.strftime('%Y%m%d')],np.datetime64(PORTSTARTDATE.strftime('%Y-%m-%d')), np.datetime64(PORTENDDATE.strftime('%Y-%m-%d')),"NO",squashparams[1]) 
                if PO2.adequatesamplebase():
                    PO2.calc(GLOBALPORTFOLIODIR)
   
                #Check Pos Definite
                if PO2.positiveDefinite():
                    pmodelweights=PO2.getdictWeights()
                    #Normalize
                    weightsum=np.sum(np.array(pmodelweights.values()),dtype=np.float64)
                    pmodelweights={key: val/weightsum for key,val in pmodelweights.iteritems()}
                    #Weighted Avg:
                    modelweights=pmodelweights
                    #Normalize
                    weightsum=np.sum(np.array(modelweights.values()),dtype=np.float64)
                    modelweights={key: val/weightsum for key,val in modelweights.iteritems()}
                    #Scale to 1 or 0.5:
                    maxweight=np.nanmax(modelweights.values())
                    print "Period "+PORTENDDATE.strftime('%Y%m%d')+": Max weight= "+str(maxweight)
                else:
                    print "USING SHARPE WEIGHTS FOR GLOBAL PORTFOLIO!!!"
                    modelweights = mean_adjusted_sharpeweights
                
                if args.globalopt == "sharpe":
                    print "USING SHARPE WEIGHTS FOR GLOBAL PORTFOLIO"
                    modelweights = mean_adjusted_sharpeweights
                #=========================================================================
                print "MODEL WEIGHTS:"
                print "----------------------------------------------"
                for  key in modelweights:
                    print str(key)+" : "+str(modelweights[key])
                print "----------------------------------------------"
                MSTATS.calcCombinedResult(modelweights) 
                print "Sharpe: "+str(MSTATS.getCombinedSharpe())
                print "Trade Freq: "+str(MSTATS.getTradeFrequence())
                print "------------------------------------------------------------"    
                #Normalize Global Weights:
                nconfigweights=dict()
                if args.globalopt == "flat":
                    if modelweights:
                        flatweight=1.0/float(len(modelweights))
                        for modelportfolioname in modelweights:
                            for config in MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)]:
                                nconfigweights[config]=MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)][config][0]*flatweight
                    weightsum=np.sum(np.array(nconfigweights.values()),dtype=np.float64)
                    nconfigweights={key: val/weightsum for key,val in nconfigweights.iteritems()}
                else:
                    if modelweights:
                        for modelportfolioname in modelweights:
                            for config in MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)]:
                                nconfigweights[config]=MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)][config][0]*modelweights[modelportfolioname]
                    weightsum=np.sum(np.array(nconfigweights.values()),dtype=np.float64)
                    nconfigweights={key: val/weightsum for key,val in nconfigweights.iteritems()}
               
                #Write Global Weights with sublib column: 
                OPTCONFIGWEIGHTS=dict()
                if modelweights:
                    for modelportfolioname in modelweights:
                        for config in MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)]:
                            #The model weights under the model has a 3rd LIB column!!! It is being added here to the optconfigweights.dat:
                            OPTCONFIGWEIGHTS[config]=(nconfigweights[config],MODELCONFIG_WEIGHTS[(PORTENDDATE.strftime('%Y%m%d'),modelportfolioname)][config][1],'1234')
                    #Write down OPTCONFIGWEIGHTS:
                    ko_util.writeWeightDict(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+PORTENDDATE.strftime('%Y%m%d')+"/optconfigweights.dat" , OPTCONFIGWEIGHTS)  
                else:
                    print "ERROR!: NO MODELS!!"
                    f=open(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+PORTENDDATE.strftime('%Y%m%d')+"/ERROR_NO_MODELS",'w')
                    f.write("Error no models\n")
                    f.close()
            else:
                print "ERROR!: NO MODELS!!"
                f=open(GLOBALPORTFOLIODIR+"/GLOBALSELECTION"+PORTENDDATE.strftime('%Y%m%d')+"/ERROR_NO_MODELS",'w')
                f.write("Error no models\n")
                f.close()
                #cd $GLOBALPORTFOLIODIR
                
            #done #period loop
    #done # portfolio loop
    #cd $BASEDIR

if __name__ == "__main__":
    sys.exit(main())

#/dat/matterhorn/production/portfolios/generate/EU_UK_US_portfolios/fullsignal/FULLEURO_6B_Crash_wq

#/dat/matterhorn/bin/scripts/python/createPortfolio_WQ.py --sublibfile sublib.dat --pwindow 200 --portfolios 1 --stime 08:00:00 --etime 21:00:00 --sdate 20180101  --edate 20190525 --grid 60Min --segment 0800_2100 --noprocesses 30 --sfb 0.1 --smb 1 --tfb 20 --gridbase 0 --squashparam 10,10 --driftfilter 1200 --weight_mul 20 --config_wbound 1 --model_wbound 10 --symbol_wbound 20 --eventfile eventremoval_fullday --capacity True
