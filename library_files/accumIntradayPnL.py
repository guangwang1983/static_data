intradayFile = open("IntradayResult_R.out_20220928")
sumPnl = 0
accumIntradayFile = open("Accum_IntradayResult_R.out_20220928", "w")
for line in intradayFile:
    if line[0] != "D":
        time = line.split(";")[0]
        pnl = float(line.split(";")[1])
        sumPnl = sumPnl + pnl
        accumIntradayFile.write(time + ";" + str(sumPnl) + "\n")
accumIntradayFile.close()
intradayFile.close()
