import pandas as pd

import methodes
from Solver import Solver
from algoGeneticTournee import algoGenConvertisseur
from alns import alnsConvertisseur
from apiRO import routeOptimization
from plne import VRPTWmip
from parser import parse_collecteurs, parse_clients
import time


def value(solution, mode):
    dist = 0
    for i in range(len(solution) - 1):
        dist += methodes.distance(solution[i].localisation, solution[i + 1].localisation, mode)
    return dist


def routing(route):
    if not route:
        print("Chemin vide")
        return ""
    chemin = "{i}".format(i=route[0].indice)
    for client in route[1:]:
        chemin += " -> {i}".format(i=client.indice)
    print("Chemin : {chemin}".format(chemin=chemin))
    return chemin


if __name__ == "__main__":
    # FILE
    file = open("comparaison.csv", "w+")
    file.write("Instance;Nbr points;Methode;Distance;Temps;Chemin\n")

    # INSTANCE
    instance = 'Hub3'
    collecteurs = parse_collecteurs("data/vehicule.json")
    collecteur = collecteurs[0]

    # SOLVERS
    solverAlns = Solver(alnsConvertisseur)
    solverGen = Solver(algoGenConvertisseur)
    solverAPI = Solver(routeOptimization)
    solverMip = Solver(VRPTWmip)

    # solvers = [solverAlns, solverGen, solverAPI, solverMip]
    # noms = ["ALNS", "AlgoGen", "RO_API", "MIP"]
    solvers = [solverAlns, solverGen, solverAPI]
    noms = ["ALNS", "AlgoGen", "RO_API"]

    list_solvers = []
    list_noms = []
    for i in range(len(solvers)):
        list_solvers.append(solvers[i])
        list_noms.append(noms[i])

    first = True

    for i in range(2):
        if first:
            clients = parse_clients("data/points51222.csv", pd.Timestamp(year=2022, month=12, day=5))
            first = False
        else:
            clients = parse_clients("data/points80123.csv", pd.Timestamp(year=2023, month=1, day=8))

        # SELECTION DE POINTS
        selection = []
        clients.sort(key=lambda x: (x.priorite(), x.capacite), reverse=True)
        while clients and clients[0].priorite() > 0.4:
            selection.append(clients.pop(0))

        nbr = str(len(selection))

        for i, s in enumerate(list_solvers):
            for j in range(10):
                print("Solving", instance, "with", list_noms[i])
                start = time.perf_counter()
                solution = s.solve(selection, collecteur)
                tps = time.perf_counter() - start
                distance = value(solution, collecteur.vehicule_type)
                line = instance + ";" + nbr + ";" + list_noms[i] + ";" + str(distance) + ";" + str(tps) + ";" + routing(solution) + "\n"
                file.write(line)
                time.sleep(10)

        """print("Solving", instance, "with MIP")
        start = time.perf_counter()
        solution = solverMip.solve(selection, collecteur)
        tps = time.perf_counter() - start
        distance = value(solution, collecteur.vehicule_type)
        line = instance + ";" + nbr + "; MIP ;" + str(distance) + ";" + str(tps) + ";" + routing(solution) + "\n"
        file.write(line)
        routing(solution)"""
