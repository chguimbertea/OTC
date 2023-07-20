import methodes
from algoGeneticTournee import algoGenConvertisseur
from apiRO import routeOptimization
from plne import VRPTWmip
from Solver import Solver
from alns import alnsConvertisseur
from parser import parse_collecteurs, parse_clients
import time

from preview import preview, previewConvexHull


def print_route(route):
    if not route:
        print("Chemin vide")
        return
    chemin = "{i}".format(i=route[0].indice)
    for client in route[1:]:
        chemin += " -> {i}".format(i=client.indice)
    print("Chemin : {chemin}".format(chemin=chemin))


def value(solution, mode):
    dist = 0
    for i in range(len(solution)-1):
        dist += methodes.distance(solution[i].localisation, solution[i + 1].localisation, mode)
    return dist


def test_select(collecteurs, clients, methode):
    solver = Solver(methode)
    solution = solver.preprocess(clients, collecteurs)
    for s in solution.keys():
        print("\nCollecteur : {n}".format(n=s.nom))
        print_route(solution[s])
        previewConvexHull(solution[s], listAllClient=clients)


if __name__ == "__main__":
    nom = 'Janv'
    collecteurs = parse_collecteurs("data/vehicule.json")
    clients = parse_clients("data/points80123.csv")
    # clients = parse_clients("data/points60.csv")

    # ALNS
    methode = alnsConvertisseur
    # ALGO GENETIQUE
    # methode = algoGenConvertisseur
    # ROUTE OPTIMIZATION API
    # methode = routeOptimization
    # MIP
    # methode = VRPTWmip

    solver = Solver(methode)

    collecteur = collecteurs[0]
    selection = []
    # l = [0, 11, 12, 31, 35, 45, 47, 50, 51, 62]
    l = [0, 11, 35, 47, 50]
    for i in l:
        selection.append(clients[i])

    start = time.perf_counter()
    solution = solver.solve(selection, collecteur)

    print("Temps :", time.perf_counter()-start)
    print("Distance :", value(solution, collecteur.vehicule_type))
    print_route(solution)
    # preview(solution, collecteur, clients)

    print("\nNbr d'appel de distance :", methodes.cpt)
