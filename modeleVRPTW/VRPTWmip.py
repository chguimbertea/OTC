from mip import *
import methodes
import time

TIME_LIMIT = 600  # s
all_point = []
distance = {}


def delta(i, j):
    return distance[i, j]


def solve(list_client, collecteur, showLog=False):
    global all_point, distance
    # initialisation
    all_point = [collecteur] + list_client
    NN = len(all_point)  # nombre de points comprenant le dépôt
    NK = len(list_client)  # nombre de tournées maximal
    distance = {(i, j): methodes.distance(all_point[i].localisation, all_point[j].localisation,
                                          collecteur.vehicule_type) for i in range(NN) for j in range(NN)}
    vv = collecteur.vehicule_vitesse
    a = collecteur.horaires[0][0]
    b = collecteur.horaires[0][1]

    model = Model(name="vrtw", sense=mip.MINIMIZE, solver_name="CBC")

    x = [[[model.add_var(name="x(" + str(k) + "," + str(i) + "," + str(j) + ")", var_type=BINARY) for j in range(NN)]
          for i in range(NN)] for k in range(NK)]
    y = [model.add_var(name="y(" + str(k) + ")", var_type=BINARY) for k in range(NK)]
    z = [[model.add_var(name="z(" + str(k) + "," + str(i) + ")", lb=0, ub=collecteur.vehicule_capacite,
                        var_type=INTEGER) for i in range(NN)] for k in range(NK)]
    t = [[model.add_var(name="t(" + str(k) + "," + str(i) + ")", lb=0, ub=b,
                        var_type=CONTINUOUS) for i in range(NN)] for k in range(NK)]
    u = [[[model.add_var(name="u(" + str(k) + "," + str(i) + "," + str(e) + ")", var_type=BINARY)
           for e in range(len(all_point[i].horaires))] for i in range(NN)] for k in range(NK)]

    model.objective = minimize(xsum(delta(i, j)*x[k][i][j] for j in range(NN) for i in range(NN) for k in range(NK)))

    # un passage
    for i in range(1, NN):
        model += (xsum(x[k][i][j] for j in range(NN) for k in range(NK)) == 1)

    for k in range(NK):
        # flot
        for i in range(1, NN):
            model += (xsum(x[k][j][i] for j in range(NN)) == xsum(x[k][i][j] for j in range(NN)))
        # pas de surplace
        for i in range(NN):
            model += (x[k][i][i] == 0)
        # depart depot
        model += (xsum(x[k][0][i] for i in range(1, NN)) == y[k])
        # arrive depot
        model += (xsum(x[k][i][0] for i in range(1, NN)) == y[k])

        # capacite
        vc = collecteur.vehicule_capacite
        model += (z[k][0] == 0)
        for i in range(1, NN):
            model += (z[k][i] <= vc * y[k])
            for j in range(NN):
                if i == j:
                    continue
                model += (z[k][j] + all_point[i].quantite >= z[k][i] - vc*(1-x[k][j][i]))
                model += (z[k][j] + all_point[i].quantite <= z[k][i] + vc*(1-x[k][j][i]))

    # temps de service en heure !!

    # depart de la premiere route : k = 0, i = 0
    for j in range(1, NN):
        trajet = delta(0, j) / vv
        model += (t[0][j] >= a + trajet - (a + trajet) * (1 - x[0][0][j]))

    # depart d'une autre route : i = 0
    for k in range(1, NK):
        service = 0.25  # temps de décharge !!
        for j in range(1, NN):
            trajet = delta(0, j) / vv
            model += (t[k][j] >= t[k - 1][0] + service + trajet - (b + service + trajet) * (1 - x[k][0][j]))

        # ordre des routes
        model += (t[k - 1][0] <= t[k][0])

    for k in range(NK):
        for i in range(1, NN):
            for j in range(NN):
                if i == j:
                    continue
                service = collecteur.temps_collecte_fixe + collecteur.temps_collecte_caisse * all_point[i].quantite
                service = service / 60  # attention en heure !!
                trajet = delta(i, j)/vv
                model += (t[k][j] >= t[k][i] + service + trajet - (b + service + trajet)*(1-x[k][i][j]))

    # horaires
    for k in range(NK):
        model += (t[k][0] >= a)
        model += (t[k][0] <= b)
        for i in range(1, NN):
            for e in range(len(all_point[i].horaires)):
                aa = all_point[i].horaires[e][0]
                bb = all_point[i].horaires[e][1]
                model += (t[k][i] >= aa - aa*(1-u[k][i][e]))
                model += (t[k][i] <= bb + (b-bb)*(1-u[k][i][e]))
            model += (xsum(u[k][i][e] for e in range(len(all_point[i].horaires))) == 1)

    if showLog :
        model.write("vrptw.lp")

    # Limitation du nombre de processeurs
    model.threads = 1

    # Lancement du chronomètre
    start = time.perf_counter()

    # Résolution du modèle
    status = model.optimize(max_seconds=TIME_LIMIT)

    # Arrêt du chronomètre et calcul du temps de résolution
    runtime = time.perf_counter() - start

    print("\n----------------------------------")
    if status == OptimizationStatus.OPTIMAL:
        print("Status de la résolution: OPTIMAL")
    elif status == OptimizationStatus.FEASIBLE:
        print("Status de la résolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print("Status de la résolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
    elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
        print("Status de la résolution: IRREALISABLE")
    elif status == OptimizationStatus.UNBOUNDED:
        print("Status de la résolution: NON BORNE")

    print("Temps de résolution (s) : ", runtime)
    print("----------------------------------")

    # Si le modèle a été résolu à l'optimalité ou si une solution a été trouvée dans le temps limite accordé
    solution = []
    if model.num_solutions > 0:
        print("Solution calculée")
        print("-> Valeur de la fonction objectif : ", model.objective_value)
        print("-> Meilleure borne inférieure = ", model.objective_bound)
        sigma = [i for i in range(NN)]
        for k in range(NK):
            if (y[k].x >= 0.5):
                for i in range(NN):
                    for j in range(NN):
                        if (x[k][i][j].x >= 0.5):
                            sigma[i] = j

        solution.append(all_point[0])
        i = -NN
        while i != 0:
            i = sigma[i]
            solution.append(all_point[i])
    else:
        print("Pas de solution calculée")
    print("----------------------------------\n")

    return solution

