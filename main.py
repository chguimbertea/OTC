import webbrowser

import folium

import methodes
from Solver import Solver
from algoGeneticTournee import algoGenConvertisseur
from alns import alnsConvertisseur
from parser import parse_collecteurs, parse_clients
from preview import preview, previewConvexHull
import time


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


def test_medium():
    nom = "Medium6"
    collecteur = parse_collecteurs("data/" + nom + "/vehicle.json")[0]
    clients = parse_clients("data/" + nom + "/points.csv")
    solution = alnsConvertisseur.solve(clients, collecteur)
    print_route(solution)


if __name__ == "__main__":
    nom = 'Hub'
    collecteurs = parse_collecteurs("data/vehicle.json")
    clients = parse_clients("data/points60.csv")

    collecteur = collecteurs[0]
    selection = []
    for i in [0, 11, 12, 31, 35, 45, 47, 50, 51, 62]:
        selection.append(clients[i])

    # ALNS
    solver = Solver(alnsConvertisseur)
    # ALGO GENETIQUE
    # solver = Solver(algoGenConvertisseur)

    # SELECTION
    # solution = solver.preprocess(clients, collecteurs)
    # for s in solution.keys():
    #     print("\nCollecteur : {n}".format(n=s.nom))
    #     print_route(solution[s])
    #     previewConvexHull(solution[s], listAllClient=clients)

    start = time.perf_counter()
    solution = solver.solve(selection, collecteur)

    print("Temps :", time.perf_counter()-start)
    print("Distance :", value(solution, collecteur.vehicule_type))
    print_route(solution)
    preview(solution, collecteur, clients)

    print("\nNbr d'appel de distance :", methodes.cpt)
