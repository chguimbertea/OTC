from algoGeneticTournee import algo


def solve(list_client, collecteur):
    algo.setup(list_client, collecteur)
    for i in range(50):
        algo.run()
    return algo.getBestSolution()
