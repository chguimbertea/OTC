import os.path
import pandas as pd


def toCsv(alns, outputPath="./result/", outputName=None, reset=False):
    if outputName is None:
        outputName = alns.instance.name
    fileName = outputPath + "alns_" + outputName + ".csv"

    if not os.path.isfile(fileName) or reset:
        with open(fileName, "w") as outfile:
            line = "Name; Evolution_cost; Evolution_iter_best; Evolution_time_best; Cost_best; Iter_best; Time_best; " \
                   "Number of iterations"
            for method in alns.USED_METHODS:
                line += "; " + method
            outfile.write(line + "\n")
    with open(fileName, "a") as outfile:
        line = "{name}; {evolution_cost}; {evolution_iter_best}; {evolution_time_best}; {cost_best}; {iter_best}; " \
               "{time_best}; {nIter}".format(name=alns.instance.name,
                                             evolution_cost=alns.evolution_cost,
                                             evolution_iter_best=alns.evolution_iter_best,
                                             evolution_time_best=alns.evolution_time_best,
                                             cost_best=alns.evolution_cost[-1],
                                             iter_best=alns.evolution_iter_best[-1],
                                             time_best=alns.evolution_time_best[-1],
                                             nIter=alns.nIter
                                             )
        for method in alns.USED_METHODS:
            value = 100 * alns.USED_METHODS_UNTIL_LAST_BEST[method] / alns.evolution_iter_best[-1]
            line += "; " + str(round(value, 1))
        outfile.write(line + "\n")
    print("ALNS is saved in " + fileName)


def toXlsx(alns, outputPath="./result/", outputName=None, reset=False):
    if outputName is None:
        outputName = alns.instance.name
    fileName = outputPath + "alns_" + outputName + ".xlsx"

    if not os.path.isfile(fileName) or reset:
        dfResult = pd.DataFrame()
    else:
        dfResult = pd.read_excel(fileName)

    newdf = pd.DataFrame()
    print(alns.instance.name)
    newdf['Instance'] = [alns.instance.name]
    print(newdf['Instance'])
    newdf['Evolution_cost'] = [alns.evolution_cost]
    newdf['Evolution_iter_best'] = [alns.evolution_iter_best]
    newdf['Evolution_time_best'] = [alns.evolution_time_best]
    newdf['Cost_best'] = alns.evolution_cost[-1]
    newdf['Iter_best'] = alns.evolution_iter_best[-1]
    newdf['Time_best'] = alns.evolution_time_best[-1]
    newdf['Iterations'] = alns.nIter
    for k in alns.USED_METHODS:
        newdf[k] = round(100 * alns.USED_METHODS_UNTIL_LAST_BEST[k] / alns.evolution_iter_best[-1], 1)
    dfResult = pd.concat([dfResult, newdf], ignore_index=True)
    dfResult.to_excel(fileName)
    print("ALNS is saved in " + fileName)
