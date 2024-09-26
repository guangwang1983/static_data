#!/usr/bin/python2.7
import os,sys
import json
from datetime import datetime
import pandas as pd
import fxstreet_figures


if __name__ == '__main__':
    fxstreet_figures.writeDailyFiles(sys.argv[1])

