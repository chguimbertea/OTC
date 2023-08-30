import pandas as pd
import methodes
from algoGeneticTournee import algoGenConvertisseur
from apiRO import routeOptimization
from plne import VRPTWmip
from Solver import Solver
from alns import alnsConvertisseur
from parser import parse_collecteurs, parse_clients
import time

from preview import preview, previewConvexHull, previewSelection


def print_route(route, aff_nom=False):
    if not route:
        print("Chemin vide")
        return
    if aff_nom:
        print("Liste :")
        print(route[0].nom, route[0].priorite())
    chemin = "{i}".format(i=route[0].indice)
    for client in route[1:]:
        if aff_nom:
            print(client.nom, client.priorite())
        chemin += " -> {i}".format(i=client.indice)
    print("Chemin : {chemin}".format(chemin=chemin))


def value(solution, mode):
    dist = 0
    for i in range(len(solution)-1):
        dist += methodes.distance(solution[i].localisation, solution[i + 1].localisation, mode)
    return dist


if __name__ == "__main__":
    """nom = 'Dec'
    jour = pd.Timestamp(year=2022, month=12, day=5)
    clients = parse_clients("data/points51222.csv", jour)"""

    nom = 'Janv'
    jour = pd.Timestamp(year=2023, month=1, day=8)
    clients = parse_clients("data/points80123.csv", jour)

    collecteurs = parse_collecteurs("data/vehicule.json")

    # ALNS
    methode = alnsConvertisseur
    # ALGO GENETIQUE
    # methode = algoGenConvertisseur
    # ROUTE OPTIMIZATION API
    # methode = routeOptimization
    # MIP
    # methode = VRPTWmip

    solver = Solver(methode)

    modes = ['rien', 'selection', 'resolution', 'combo']
    mode = modes[2]

    if mode == 'selection':
        print("Prépocessus en cours...")
        # solution = solver.selection(clients, collecteurs, methode_int=0)
        solution = solver.preprocess(clients, collecteurs)
        for s in solution.keys():
            print("\nCollecteur : {n}".format(n=s.nom))
            print_route(solution[s], True)
            print("Valeur :", methodes.fitness_single_routing(solution[s], s, clients))
        print("Valeur :", methodes.fitness_multiple_routing(solution, clients))
        previewSelection(solution, clients)

    if mode == 'resolution':
        print("Résolution en cours...")
        selection = []
        clients.sort(key=lambda x: (x.priorite(), x.capacite), reverse=True)
        while clients and clients[0].priorite() > 0.4:
            selection.append(clients.pop(0))
            print(selection[-1].indice, selection[-1].quantite, selection[-1].capacite, selection[-1].horaires)
        collecteur = collecteurs[0]
        start = time.perf_counter()
        solution = solver.solve(selection, collecteur)

        print("Temps :", time.perf_counter() - start)
        print("Distance :", value(solution, collecteur.vehicule_type))
        print_route(solution)
        # preview(solution, collecteur, clients)

    print("\nNbr d'appel de distance :", methodes.cpt)
