#!/usr/bin/python2.7
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
import multiprocessing
from portfolio_functions import *
from copy import deepcopy
#Standard np.datetime64 format (notice the T):
#"YYYY-mm-ddTHH:MM:SS"



def main(argv=None):
    if argv is None:
        argv = sys.argv
    #echo "-portfoliosfile <filename> -updatefreq <update freq in days> -oosstart <First oos date> -pwindow <PORTFOLIO WINDOW> -portfolios <PORTFOLIONO> -datesfile <datesfile> -gpweights <COV/SHARPE>" 
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", help="0-1.0=flat.1=cov.", required=True)
    args = parser.parse_args(argv[1:])
    
    BASEDIR=os.getcwd()

    SEGMENTS=glob.glob(BASEDIR+"/"+"SEGMENT*GLOBALPORTFOLIO[12345]*")
    for segdir in SEGMENTS: 
        os.chdir(segdir)
        for globdir in glob.glob("GLOBAL*"):
            os.chdir(globdir)
            print os.getcwd()
            #optconfigweights.dat 
            if os.path.exists("optconfigweights.dat") and os.path.exists("optconfigweights_flat.dat"):
                covdict = ko_util.readWeightDict("optconfigweights.dat")     
                flatdict = ko_util.readWeightDict("optconfigweights_flat.dat")     
                flatdict_sum=sum([float(flatdict[key][0]) for key in flatdict])
                norm_flatdict=dict()
                for key in flatdict:
                    norm_flatdict[key]=float(flatdict[key][0])/float(flatdict_sum)
                alphadict=dict()
                for key in covdict:
                    alphadict[key]= (float(args.alpha)*float(covdict[key][0]) + (1.0-float(args.alpha))*float(norm_flatdict[key]),covdict[key][1])
                ko_util.writeWeightDict(segdir+"/"+globdir+"/optconfigweights_alpha"+args.alpha+".dat",alphadict)
            os.chdir(segdir)


if __name__ == "__main__":
    sys.exit(main())
