from Solver import Solver
from alns import alnsConvertisseur
from parser import parse_collecteurs, parse_clients


def print_route(route):
    if not route:
        print("Chemin vide")
        return
    chemin = "{i}".format(i=route[0].indice)
    for client in route[1:]:
        chemin += " -> {i}".format(i=client.indice)
    print("Chemin : {chemin}".format(chemin=chemin))


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

    solver = Solver(alnsConvertisseur)
    # solution = solver.solve(selection, collecteur)
    # print_route(solution)
    solution = solver.preprocess(clients, collecteurs)
    for s in solution.keys():
        print("Collecteur : {n}".format(n=s.nom))
        print_route(solution[s])

