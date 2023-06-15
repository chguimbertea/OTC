import methodes
import routeOptimizationConvertisseur
from Solver import Solver
from algoGeneticTournee import algoGenConvertisseur
from alns import alnsConvertisseur
from parser import parse_collecteurs, parse_clients
import time


def value(solution, mode):
    dist = 0
    for i in range(len(solution) - 1):
        dist += methodes.distance(solution[i].localisation, solution[i + 1].localisation, mode)
    return dist


if __name__ == "__main__":
    # FILE
    file = open("comparaison.csv", "w+")
    file.write("Instance;Nbr points;Methode;Distance;Temps\n")

    # INSTANCE
    instance = 'Hub3'
    collecteurs = parse_collecteurs("data/vehicle.json")
    clients = parse_clients("data/points60.csv")
    collecteur = collecteurs[0]
    selection = []
    for i in [0, 11, 35, 47, 50]:
        selection.append(clients[i])

    # SOLVERS
    solverAlns = Solver(alnsConvertisseur)
    solverGen = Solver(algoGenConvertisseur)
    solverAPI = Solver(routeOptimizationConvertisseur)

    list_solvers = [solverAlns, solverGen, solverAPI]
    list_noms = ["ALNS", "AlgoGen", "RO_API"]
    nbr = str(len(selection))

    for i, s in enumerate(list_solvers):
        print("Solving", instance, "with", list_noms[i])
        dist_moy = 0
        tps_moy = 0

        for j in range(10):
            start = time.perf_counter()
            solution = s.solve(selection, collecteur)
            tps = time.perf_counter() - start
            dist = value(solution, collecteur.vehicule_type)
            file.write(instance + ";" + nbr + ";" + list_noms[i] + ";" + str(dist) + ";" + str(tps) + "\n")

            dist_moy += dist
            tps_moy += tps

        print("Distance :", dist_moy/10)
        print("Temps :", tps_moy/10)
