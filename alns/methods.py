"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
import random
import math
from alns.SolutionChecker import check


def fast_check(listClient, ntm, rpt, dtm):
    if not listClient:
        print("No client")
        return False
    if ntm <= 0 or rpt <= 0 or dtm <= 0:
        print("No solution can satisfy parameters numberTimeSlotMax = {ntm}, routePerTimeSlotMax = {rpt}, "
              "durationTimeSlotMax = {dtm}".format(ntm=ntm, rpt=rpt, dtm=dtm))
        return False
    for client in listClient:
        isOpen = False
        for hours in client.businessHours:
            if hours and hours[0] < hours[1]:
                isOpen = True
                break
        if not isOpen:
            print("Client n°{i} : {name}, isn't open today".format(i=client.indice, name=client.name))
            return False
    return True


def acceptance_criteria_greedy(currentSolution, testSolution):
    """
    FR:
    Retourne True si on accepte la solution et False sinon.

    EN :
    Returns True if the solution is accepted and False otherwise.
    """
    return currentSolution.getCost() < testSolution.getCost()


def acceptance_criteria_simulated_annealing(currentSolution, testSolution, T0, alpha, step, onremontelapente=0):
    """
    FR:
    Retourne True si on accepte la solution et False sinon. On a la possibilité ici d'accepter une solution
    moins bonne avec une probabilité p

    EN :
    Returns True if the solution is accepted and False otherwise. We have the possibility here to accept a
    worst solution with probability p
    """
    delta = currentSolution.getCost() - testSolution.getCost()
    if delta <= 0:
        return True
    else:
        r = random.random()
        cst = T0 * (alpha ** step)
        if cst != 0:
            p = math.exp(- (delta / cst))
        else:
            p = 1.1
        # print(delta,T0,alpha,step)
        if r < p:
            onremontelapente += 1
            return True
        else:
            return False


def order_ListClient_random(listClient):
    """
    FR :
    Tri de la liste des clients de manière aléatoire

    EN :
    Sort randomly the list of clients
    """
    random.shuffle(listClient)
    return listClient


def order_ListClient_by_ratio(listClient):
    """
    FR :
    Tri de la liste des clients dans l'ordre decroissant des ratios

    EN :
    Sort the list of clients in descending order of ratios
    """
    listClient.sort(key=lambda x: x.ratio(), reverse=True)
    return listClient


def swap_two_client(routeA, routeB):
    # Récupération des positions dans les trajets
    positionA = random.randint(1, len(routeA.trajet) - 2)
    positionB = random.randint(1, len(routeB.trajet) - 2)

    # Assignation des valeurs de client A et B
    clientA = routeA.getClientByIndex(positionA)
    clientB = routeB.getClientByIndex(positionB)

    # Assignation du client B à la route A
    routeA.insertClient(positionA, clientB)
    # Suppression du client A de la route A
    routeA.removeClientByPosition(positionA + 1)

    # Assignation du client A à la route B
    routeB.insertClient(positionB, clientA)
    # Suppression du client B de la route B
    routeB.removeClientByPosition(positionB + 1)


def swap_intra_route(solution, listClient):
    """ SWAP INTRA ROUTE
    FR :
    échange de deux clients au sein d'une meme route

    EN :
    exchange two clients within the same route
    """
    # Copie de la solution initiale
    solutionInitiale = solution.copy()

    # initialisation des variables
    nbIteration = 0
    nbIterationMax = 10
    solutionInitaleAssigned = True

    # Tant qu'on n'a pas fait 10 itérations et (que la solution est incompatible ou que la solution
    # initiale a été réassignée)
    while nbIteration < nbIterationMax and (not check(solution, listClient) or solutionInitaleAssigned):
        solutionInitaleAssigned = False

        # Récupération des time slots à switcher
        possibleTimeSlot = solution.listTimeSlot.copy()
        possibleRoute = []
        while possibleTimeSlot:
            timeSlot = random.choice(possibleTimeSlot)
            for route in timeSlot.listRoute:
                if len(route.trajet) >= 4:
                    possibleRoute.append(route)
            if possibleRoute:
                break
            else:
                possibleTimeSlot.remove(timeSlot)
        if not possibleRoute:
            return

        route = random.choice(possibleRoute)

        swap_two_client(route, route)

        # Vérification de la solution
        if not check(solution, listClient):
            # Si la solution n'est pas compatible alors on réaffecte la solution de départ
            solutionInitaleAssigned = True
            solution.clone(solutionInitiale)
        nbIteration += 1

    # Vérification de la solution
    if not check(solution, listClient):
        # Si la solution n'est pas compatible alors on réaffecte la solution de départ
        solution.clone(solutionInitiale)


def swap_inter_route(solution, listClient):
    """ SWAP INTER ROUTE
    FR :
    échange de deux clients au sein de deux routes strictement differentes

    EN :
    exchange two clients within two strictly different routes
    """
    # Copie de la solution initiale
    solutionInitiale = solution.copy()

    # initialisation des variables
    nbIteration = 0
    nbIterationMax = 10
    solutionInitaleAssigned = True
    routes_vides = 0
    for timeslot in solution.listTimeSlot:
        for route in timeslot.listRoute:
            if len(route.trajet) < 3:
                routes_vides += 1

    nRoute = sum([len(i.listRoute) for i in solution.listTimeSlot])
    if nRoute <= 2 and routes_vides != 0:
        return

    # Tant qu'on n'a pas fait 10 itérations et (que la solution est incompatible ou que la solution
    # initiale a été réassignée)
    while nbIteration < nbIterationMax and (not check(solution, listClient) or solutionInitaleAssigned):
        solutionInitaleAssigned = False

        # Récupération des time slots à switcher
        timeSlotA = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]
        timeSlotB = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]

        while timeSlotB == timeSlotA and len(timeSlotA.listRoute) < 2:
            timeSlotA = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]

        # Récupération des routes dans les time slots
        routeA = timeSlotA.listRoute[random.randint(0, len(timeSlotA.listRoute) - 1)]
        routeB = timeSlotB.listRoute[random.randint(0, len(timeSlotB.listRoute) - 1)]
        while routeB == routeA:
            routeB = timeSlotB.listRoute[random.randint(0, len(timeSlotB.listRoute) - 1)]

        swap_two_client(routeA, routeB)

        # Vérification de la solution
        if not check(solution, listClient):
            # Si la solution n'est pas compatible alors on réaffecte la solution de départ
            solutionInitaleAssigned = True
            solution.clone(solutionInitiale)
        nbIteration += 1

    # Vérification de la solution
    if not check(solution, listClient):
        # Si la solution n'est pas compatible alors on réaffecte la solution de départ
        solution.clone(solutionInitiale)


def choose_destroy_method(destroy_methods, Weights_destroy):
    """
    FR :
    Fonction choisissant une méthode de destruction suivant les probabilités associées

    EN :
    Function choosing a destruction method according to the associated probabilities
    """
    s = sum(Weights_destroy.values())
    if s <= 1:
        s = 1
    proba = [Weights_destroy[i] / s for i in Weights_destroy]
    destroy = random.choices(destroy_methods, proba)
    return destroy[0]


def choose_repair_method(repair_methods, Weights_repair):
    """
    FR:
    Fonction choisissant une méthode de reconstruction suivant les probabilités associées

    EN:
    Function choosing a repair method according to the associated probabilities
    """
    s = sum(Weights_repair.values())
    proba = [Weights_repair[i] / s for i in Weights_repair]
    repair = random.choices(repair_methods, proba)
    return repair[0]


def update_weights_by_dict(listName, listUsed, listSuccess, rho):
    for i in listName:
        if listUsed[i] != 0:
            listName[i] = ((1 - rho) * listName[i]) + (rho * (listSuccess[i] / listUsed[i]))
        else:
            listName[i] = (1 - rho) * listName[i]


def update_weights(rho, Weights_destroy, Weights_repair, Success_destroy, Success_repair, Used_destroy_methods,
                   Used_repair_methods):
    """
    FR:
    Mise à jour des poids des methodes de destruction et de repair suivant les formules expliquées dans le rapport

    EN:
    Updating the weights of the destruction and repair methods according to the formulas explained in the report
    """
    update_weights_by_dict(Weights_destroy, Used_destroy_methods, Success_destroy, rho)
    update_weights_by_dict(Weights_repair, Used_repair_methods, Success_repair, rho)

    return Weights_destroy, Weights_repair
