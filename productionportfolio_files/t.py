
#-----------------------------------------------------------
    #Portfolio Period update (optconfigweights.dat,etc)
    #-----------------------------------------------------------
    portfolios_arg_dict=ko_util.readDbDict(args.multiportfoliopath+"/portfolio_args_dict.def")
    #-----------------------------------------------------------
    print args.multiportfoliopath+"/period"+thisfriday_date
    print "#-----------------------------------------------------------"
    symbolpathlist=glob.glob(args.multiportfoliopath+"/symbol_pnl/*.*")
    for symbol in symbolpathlist:
        print symbol
        os.system("cat "+symbol+"/DailyResult.out | grep -v DATE | sort -t \";\" -gk1 | uniq > pnltemp.dat")
        os.system("echo \"DATE;PNL\" > "+symbol+"/DailyResult.out")
        os.system("cat pnltemp.dat >> "+symbol+"/DailyResult.out")
        roos=open(symbol+"/DailyResult.out","r")
        rooslines=roos.readlines()
        new_roos=rooslines[0]
        for rline in rooslines[1:]:
            arr=rline.strip().split(";")
            if int(arr[0]) <= int(lastfriday_date):
                new_roos+=rline
        nroosfile=open(symbol+"/DailyResult.out","w")
        nroosfile.write(new_roos)
        nroosfile.close()

