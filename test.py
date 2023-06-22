import VRPTWmip
import methodes
import routeOptimization
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
    solverAPI = Solver(routeOptimization)
    solverMip = Solver(VRPTWmip)

    solvers = [solverAlns, solverGen, solverAPI, solverMip]
    noms = ["ALNS", "AlgoGen", "RO_API", "MIP"]

    list_solvers = []
    list_noms = []
    for i in [0, 1]:
        list_solvers.append(solvers[i])
        list_noms.append(noms[i])

    nbr = str(len(selection))

    for j in range(10):
        for i, s in enumerate(list_solvers):
            print("Solving", instance, "with", list_noms[i])
            start = time.perf_counter()
            solution = s.solve(selection, collecteur)
            tps = time.perf_counter() - start
            distance = value(solution, collecteur.vehicule_type)
            file.write(instance + ";" + nbr + ";" + list_noms[i] + ";" + str(distance) + ";" + str(tps) + "\n")
        #time.sleep(30)
