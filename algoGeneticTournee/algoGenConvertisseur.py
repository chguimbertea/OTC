from algoGeneticTournee import algo


def solve(list_client, collecteur, showLog=False):
    nbGeneration = 10
    nbPopulation = 1000
    tauxMutation = 0.1
    algo.setup(list_client, collecteur, nbPopulation, tauxMutation)
    for i in range(nbGeneration):
        algo.run(showLog)
    return algo.getBestSolution()
