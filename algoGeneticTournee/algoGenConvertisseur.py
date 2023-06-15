from algoGeneticTournee import algo


def solve(list_client, collecteur, showLog=False):
    algo.setup(list_client, collecteur)
    for i in range(20):
        algo.run(showLog)
    return algo.getBestSolution()
