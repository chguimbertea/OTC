"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
import random
import alns.methods as methods
from alns.Route import Route
from alns.TimeSlot import TimeSlot
from alns.SolutionChecker import check


def get_missing_client_list(listTimeSlot, listClient):
    listClientMissing = []
    for timeSlot in listTimeSlot:
        for route in timeSlot.listRoute:
            for client in route.trajet:
                client.setVisited()

    # Réinitialisation des attributs visited des clients
    for client in listClient:
        if not client.isVisited():
            listClientMissing.append(client)
        client.setNotVisited()
    return listClientMissing


def get_new_route(vehicle, clientMissing=None):
    # Création de la nouvelle route 0 => clientMissing => 0
    newRoute = Route(vehicle)
    if clientMissing is not None:
        newRoute.appendClient(clientMissing)
    return newRoute


def get_new_timeSlot(vehicle, clientMissing=None):
    newTimeSlot = TimeSlot()
    newRoute = get_new_route(vehicle, clientMissing)

    # Ajout de la route au time slot
    newTimeSlot.appendRoute(newRoute)

    return newTimeSlot


def find_position_on_route(solution, listClient, route, clientMissing, nbIterations):
    bound = max(1, len(route.trajet) - 2)
    position = random.randint(1, bound)
    if route.getTotalQuantity() + clientMissing.quantity < route.vehicle.capacity:
        # Ajout du client
        route.insertClient(position, clientMissing)

        # Si la solution n'est pas compatible on enlève le client
        if not check(solution, listClient, False, True):
            route.removeClientByPosition(position)
            nbIterations += 1
        else:
            return True
    return False


def find_position(solution, listClient, clientMissing, vehicle, numberTimeSlotMax, routePerTimeSlotMax):
    positionFound = False
    for timeSlot in solution.listTimeSlot:
        for route in timeSlot.listRoute:
            # Si l'ajout de clientMissing est possible au niveau capacité alors on essaie toutes les positions
            if clientMissing.quantite + route.getTotalQuantity() <= route.vehicle.capacity:
                # si la route est vide :
                if len(route.trajet) == 2:
                    route.insertClient(1, clientMissing)

                    # Si la solution est compatible alors on sort de la boucle de client
                    if check(solution, listClient, False, True):
                        positionFound = True
                        break
                    else:
                        # Sinon on supprime l'ajout
                        route.removeClientByPosition(1)

                # si la route a au moins un client
                for indiceClient in range(1, len(route.trajet) - 1):
                    route.insertClient(indiceClient, clientMissing)
                    # Si la solution est compatible alors on sort de la boucle de client
                    if check(solution, listClient, False, True):
                        positionFound = True
                        break
                    else:
                        # Sinon on supprime l'ajout
                        route.removeClientByPosition(indiceClient)
            # Si on a trouvé une position on sort de la boucle de route
            if positionFound:
                break
        if positionFound:
            break
        if not positionFound:
            # Sinon on essaie d'ajouter une route au time slot avec la position manquante
            # S'il est possible d'ajouter une route au time slot
            if len(timeSlot.listRoute) < routePerTimeSlotMax:
                # Création de la route 0 => ckientMissing => 0
                newRoute = get_new_route(vehicle, clientMissing)

                # Ajout au timeSlot courant
                timeSlot.appendRoute(newRoute)

                # Si la solution est compatible
                if check(solution, listClient, False, True):
                    # On sort de la boucle et on passe la variable positionFound à True
                    positionFound = True
                    break
                else:
                    # Sinon on supprime la route de la liste du time slot
                    timeSlot.removeRoute(newRoute)

        # Si on a trouvé une solution, on sort de la liste de time slot
        if positionFound:
            break
        if not positionFound:
            # Sinon on essaie d'ajouter un time slot si c'est possible
            if len(solution.listTimeSlot) < numberTimeSlotMax:
                # Ajout du time slot à la solution
                newTimeSlot = get_new_timeSlot(vehicle, clientMissing)
                solution.appendTimeSlot(newTimeSlot)

                # Si la solution est compatible
                if check(solution, listClient, False, True):
                    # On passe la variable à True et on sort de la boucle
                    positionFound = True
                    break
                else:
                    # Sinon on supprime le time slot de la solution
                    solution.removeTimeSlot(newTimeSlot)
    return positionFound


def best_insertion(solution, timeSlot, client, min_cost):
    indice_best_timeslot, indice_best_route, indice_best_client = None, None, None
    for route in range(len(solution.listTimeSlot[timeSlot].listRoute)):
        for indiceClient in range(1, len(solution.listTimeSlot[timeSlot].listRoute[route].trajet)):

            solution.listTimeSlot[timeSlot].listRoute[route].insertClient(indiceClient, client)
            cost = solution.getCost()
            if cost < min_cost:
                min_cost = cost
                indice_best_timeslot = timeSlot
                indice_best_route = route
                indice_best_client = indiceClient

            solution.listTimeSlot[timeSlot].listRoute[route].removeClientByPosition(indiceClient)
            solution.updateCost = True
    return min_cost, indice_best_timeslot, indice_best_route, indice_best_client


def repair_randomV2(solution, listClient, vehicle, numberTimeSlotMax, routePerTimeSlotMax, repairdontwork):
    """ REPAIR RANDOM
    FR :
    On choisit de mettre le client au hasard parmi les time slot existant et un nouveau time slot.
    Lorsqu'on a choisit le time slot, on choisit au hasard une route entre les routes existantes et une nouvelle route.
    On met ensuite le client au hasard dans la route choisie.
    On recommence jusqu'a avoir inserer tous les clients de listClientMissing

    EN :
    We choose to put the client at random among the existing time slot and a new time slot.
    When the time slot has been chosen, a route is chosen at random between the existing routes and a new route.
    Then we put the client at random in the chosen route.
    We start again until we have inserted all the clients of listClientMissing
    """
    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Mélange des positions manquantes dans un ordre aleatoire
    listClientMissing = methods.order_ListClient_random(listClientMissing)

    for clientMissing in listClientMissing:
        nbIterations = 0
        nbIterationMax = 30
        while nbIterations < nbIterationMax:
            # check(solution, listClient, False, False) #!!?
            if not solution.listTimeSlot:
                # Ajout du time slot à la solution
                newTimeSlot = get_new_timeSlot(vehicle, clientMissing)
                solution.appendTimeSlot(newTimeSlot)
                break

            else:
                bound = len(solution.listTimeSlot)
                if len(solution.listTimeSlot) + 1 > numberTimeSlotMax:
                    positionTimeSlot = random.randint(0, bound - 1)
                else:
                    positionTimeSlot = random.randint(0, bound)
                if positionTimeSlot == bound:
                    # Ajout du time slot à la solution
                    newTimeSlot = get_new_timeSlot(vehicle, clientMissing)
                    solution.appendTimeSlot(newTimeSlot)

                    if check(solution, listClient, False, True):
                        # On passe la variable à True et on sort de la boucle
                        break
                    else:
                        solution.removeTimeSlot(newTimeSlot)
                        nbIterations += 1
                else:
                    timeSlot = solution.listTimeSlot[positionTimeSlot]
                    for route in timeSlot.listRoute:
                        if len(route.trajet) <= 2:
                            timeSlot.removeRoute(route)
                    if len(timeSlot.listRoute) + 1 > routePerTimeSlotMax:
                        route = timeSlot.listRoute[random.randint(0, len(timeSlot.listRoute) - 1)]
                        if find_position_on_route(solution, listClient, route, clientMissing, nbIterations):
                            break
                    else:
                        bound = len(timeSlot.listRoute)
                        positionRoute = random.randint(0, bound)
                        if positionRoute == bound:
                            # Creation de la route 0 => ckientMissing => 0
                            newRoute = get_new_route(vehicle, clientMissing)

                            # Ajout au timeSlot courant
                            timeSlot.appendRoute(newRoute)

                            if not check(solution, listClient, False, True):
                                timeSlot.removeRoute(newRoute)
                                nbIterations += 1
                            else:
                                break
                        else:
                            route = timeSlot.listRoute[positionRoute]
                            if find_position_on_route(solution, listClient, route, clientMissing, nbIterations):
                                break
        if nbIterations >= nbIterationMax:
            repairdontwork["repair_randomV2"] += 1
            break


def repair_randomv1(solution, listClient, vehicle, repairdontwork):
    """ REPAIR RANDOM
    FR :
    Méthode de réparation aléatoire d'une solution
    1 - Recherche d'un client manquant
    2 - Ajout aléatoire du client
    3 - Vérification de la solution trouvée
    4 - Si la solution ne correspond pas, on supprime le client et on recommence à l'étape 2

    Ici on ne prend pas en compte le fait de mettre un client dans un nouveau time slot tout seul ou
    dans une route vide d'un time slot existant.

    EN :
    Random repair method of a solution
    1 - Search for a missing client
    2 - Randomly add the client
    3 - Check the solution found
    4 - If the solution doesn't match, we delete the client and start again at step 2

    Here we don't take into account the fact of putting a client in a new time slot or
    in an empty route of an existing time slot.
    """
    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Mélange des positions manquantes aleatoirement
    listClientMissing = methods.order_ListClient_random(listClientMissing)

    if not solution.listTimeSlot:
        # Ajout du time slot à la solution
        newTimeSlot = get_new_timeSlot(vehicle)
        solution.appendTimeSlot(newTimeSlot)

    cantinsert = False

    # 2 - Ajout du client à un emplacement random
    for clientMissing in listClientMissing:
        nbIterations = 0
        nbIterationMax = 50
        while nbIterations < nbIterationMax:
            # Recherche de l'endroit où l'ajouter
            if len(solution.listTimeSlot) >= 1:
                timeSlot = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]
            else:
                timeSlot = solution.listTimeSlot[0]
            if not timeSlot.listRoute:
                # Creation de la route 0 => ckientMissing => 0
                newRoute = get_new_route(vehicle, clientMissing)

                # Ajout au timeSlot courant
                timeSlot.appendRoute(newRoute)

                if check(solution, listClient, False, True):
                    # On a trouvé alors on sort de la boucle
                    break
                else:
                    # Sinon on supprime la route de la liste du time slot
                    timeSlot.removeRoute(newRoute)
                    cantinsert = True
                    break
            if cantinsert:
                break
            else:
                if len(timeSlot.listRoute) >= 1:
                    route = timeSlot.listRoute[random.randint(0, len(timeSlot.listRoute) - 1)]
                else:
                    route = timeSlot.listRoute[0]
                if len(route.trajet) >= 3:
                    position = random.randint(1, len(route.trajet) - 2)
                else:
                    position = 1

                # Si le client est ajoutable d'un point de vue capacité
                if route.getTotalQuantity() + clientMissing.quantite < route.vehicle.capacity:
                    # Ajout du client
                    route.insertClient(position, clientMissing)

                    # 3 - Vérification de la solution trouvée
                    # Si la solution n'est pas compatible on enlève le client
                    if not check(solution, listClient, False, True):
                        route.removeClientByPosition(position)
                    else:
                        break

            # Mise à jour du nombre d'itérations
            nbIterations += 1

        if cantinsert:
            break
        if nbIterations == nbIterationMax:
            repairdontwork["repair_randomv1"] += 1
            break


def repair_2_regret(solution, listClient, vehicle):
    """ REPAIR REGRET 2 HEURISTIC
    FR :
    Ici on cherche pour chaque client sont emplacement qui minimise l'augmentation du cout de la fonction objective
    lors de son insertion. On garde aussi la deuxième meilleure place d'insertion de ce client. Ensuite on insere le
    client qui a la difference la plus grande entre sa meilleure place et sa seconde meilleure place.

    EN :
    Here we look for each client to find the location that minimizes the increase in the cost of the objective function
    when it is inserted. We also keep the second best place of insertion of this client. Then we insert the client
    that has the biggest difference between its best place and its second best place.
    """
    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)
    solution.updateCost = True

    # si la solution est vide
    if not solution.listTimeSlot:
        # Ajout du time slot à la solution
        newTimeSlot = get_new_timeSlot(vehicle)
        solution.appendTimeSlot(newTimeSlot)

    # Boucle de calcul du cout de la fonction objective si on met le client
    while listClientMissing:
        Data_best_client = []
        Data_second_best_client = []
        best_client = listClientMissing[0]
        second_best_client = listClientMissing[0]

        for client in listClientMissing:
            min_cost = 10000
            min_cost_2 = 10000

            indice_best_timeslot, indice_best_route, indice_best_client = 0, 0, 0
            indice_second_best_timeslot, indice_second_best_route, indice_second_best_client = 0, 0, 0

            for timeSlot in range(len(solution.listTimeSlot)):
                for route in range(len(solution.listTimeSlot[timeSlot].listRoute)):
                    for indiceClient in range(1, len(solution.listTimeSlot[timeSlot].listRoute[route].trajet)):
                        solution.listTimeSlot[timeSlot].listRoute[route].insertClient(indiceClient, client)
                        cost = solution.getCost()
                        if cost < min_cost:
                            min_cost_2 = min_cost
                            min_cost = cost

                            indice_second_best_timeslot = indice_best_timeslot
                            indice_second_best_route = indice_best_route
                            indice_second_best_client = indice_best_client
                            second_best_client = best_client

                            indice_best_timeslot = timeSlot
                            indice_best_route = route
                            indice_best_client = indiceClient
                            best_client = client

                        solution.listTimeSlot[timeSlot].listRoute[route].removeClientByPosition(indiceClient)
                        solution.updateCost = True

            Data_best_client.append(
                [min_cost, indice_best_timeslot, indice_best_route, indice_best_client, best_client])
            Data_second_best_client.append(
                [min_cost_2, indice_second_best_timeslot, indice_second_best_route, indice_second_best_client,
                 second_best_client])

        maximum_cost = 0
        client_to_insert = Data_best_client[0][1:]
        for i in range(len(Data_best_client)):
            difference = Data_second_best_client[i][0] - Data_best_client[i][0]
            if difference > maximum_cost:
                maximum_cost = difference
                client_to_insert = Data_best_client[i][1:]

        solution.listTimeSlot[client_to_insert[0]].listRoute[client_to_insert[1]].insertClient(client_to_insert[2],
                                                                                               client_to_insert[3])

        listClientMissing.remove(client_to_insert[3])


def repair_FirstPositionAvailable_maxratio_listClient(solution, listClient, vehicle, numberTimeSlotMax,
                                                      routePerTimeSlotMax, repairdontwork):
    """ FIRST POSITION AVAILABLE MAX RATIO
    FR :
    Méthode de réparation de la solution
    1 - Recherche des clients manquants
    2 - Ajout de la position à la première place disponible dans le premier time slot
    3 - Si aucune place trouvée alors on cherche à créer une nouvelle route dans le même time slot
    4 - Si aucune place n'est trouvée alors on passe au time slot suivant
    5 - Si aucune place n'est trouvée, on essaie d'ajouter un time slot

    EN :
    Method of repairing the solution
    1 - Search for missing clients and sort this list randomly
    2 - Add the position to the first available place in the first time slot
    3 - If no place is found then we try to create a new route in the same time slot
    4 - If no place is found then we go to the next time slot
    5 - If no place is found, we try to add a time slot
    """
    solutionInitiale = solution.copy()

    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Tri de la liste selon un critère de la méthode orderListOperator
    listClientMissing = methods.order_ListClient_by_ratio(listClientMissing)

    # Initialisation des variables
    positionFound = False
    NMAX = 10
    n = 0
    while not positionFound and n < NMAX and listClientMissing != []:
        for clientMissing in listClientMissing:
            positionFound = find_position(solution, listClient, clientMissing, vehicle,
                                          numberTimeSlotMax, routePerTimeSlotMax)

            # Si aucun client n'a pu être ajouté à aucune route, aucune route créée et aucun time slot créé
            # alors on s'arrête pour cet opérateur et on sort de la méthode
            if not positionFound:
                solution.clone(solutionInitiale)
                listClientMissing = methods.order_ListClient_by_ratio(listClientMissing)
                n += 1
                break

    if n == NMAX:
        repairdontwork["repair_FirstPositionAvailable_maxratio_listClient"] += 1


def repair_FirstPositionAvailable_randomlistClient(solution, listClient, vehicle, numberTimeSlotMax,
                                                   routePerTimeSlotMax, repairdontwork):
    """ FIRST POSITION AVAILABLE RANDOM
    FR :
    Méthode de réparation de la solution
    1 - Recherche des clients manquants et tri de cette liste aleatoirement
    2 - Ajout de la position à la première place disponible dans le premier time slot
    3 - Si aucune place trouvée alors on cherche à créer une nouvelle route dans le même time slot
    4 - Si aucune place n'est trouvée alors on passe au time slot suivant
    5 - Si aucune place n'est trouvée, on essaie d'ajouter un time slot

    EN :
    Method of repairing the solution
    1 - Search for missing clients and sort this list randomly
    2 - Add the position to the first available place in the first time slot
    3 - If no place is found then we try to create a new route in the same time slot
    4 - If no place is found then we go to the next time slot
    5 - If no place is found, we try to add a time slot
    """
    solutionInitiale = solution.copy()

    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Tri de la liste selon un critère de la méthode orderListOperator
    listClientMissing = methods.order_ListClient_random(listClientMissing)

    # Initialisation des variables
    positionFound = False
    NMAX = 10
    n = 0
    while not positionFound and n < NMAX and listClientMissing != []:
        for clientMissing in listClientMissing:
            positionFound = find_position(solution, listClient, clientMissing, vehicle,
                                          numberTimeSlotMax, routePerTimeSlotMax)

            # Si on a pu ajouter aucun client à aucune route, créer aucune route et créer aucun time slot alors
            # on s'arrête pour cet opérateur et on sort de la méthode
            if not positionFound:
                solution.clone(solutionInitiale)
                listClientMissing = methods.order_ListClient_random(listClientMissing)
                n += 1
                break

    if n == NMAX:
        repairdontwork["repair_FirstPositionAvailable_randomlistClient"] += 1


def repair_random_best_insertion(solution, listClient, vehicle, numberTimeSlotMax, routePerTimeSlotMax):
    """ BEST INSERTION RANDOM
    FR :
    Pour chaque client, on cherche l'endroit qui minimise l'augmentation du cout de la fonction objective lors de son
    insertion dans la solution. La liste des clients à inserer est construite de manière aléatoire.

    EN :
    For each client, we look for the place that minimises the increase of the cost of the objective function when it is
    inserted in the solution. The list of clients to be inserted is built randomly.
    """
    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Tri de la liste selon un critère de la méthode orderListOperator
    listClientMissing = methods.order_ListClient_random(listClientMissing)

    if not solution.listTimeSlot:
        # Ajout du time slot à la solution
        newTimeSlot = get_new_timeSlot(vehicle)
        solution.appendTimeSlot(newTimeSlot)
    solution.updateCost = True

    # Boucle de calcul du cout de la fonction objective si on met le client
    for client in listClientMissing:
        min_cost = 100000
        indice_best_timeslot, indice_best_route, indice_best_client = 0, 0, 0

        if len(solution.listTimeSlot) + 1 <= numberTimeSlotMax:
            newTimeSlot = TimeSlot()

            # Ajout du time slot à la solution
            solution.appendTimeSlot(newTimeSlot)

        for timeSlot in range(len(solution.listTimeSlot)):
            if len(solution.listTimeSlot[timeSlot].listRoute) + 1 <= routePerTimeSlotMax:
                newRoute = get_new_route(vehicle)

                # Ajout au timeSlot courant
                solution.listTimeSlot[timeSlot].appendRoute(newRoute)

            min_cost, id_timeslot, id_route, id_client = best_insertion(solution, timeSlot, client, min_cost)
            if id_timeslot is not None:
                indice_best_timeslot = id_timeslot
                indice_best_route = id_route
                indice_best_client = id_client

        solution.listTimeSlot[indice_best_timeslot].listRoute[indice_best_route].insertClient(indice_best_client,
                                                                                              client)


def repair_max_ratio_best_insertion(solution, listClient, vehicle):
    """ BEST INSERTION MAX RATIO
    FR :
    Pour chaque client, on cherche l'endroit qui minimise l'augmentation du cout de la fonction objective lors de son
    insertion dans la solution. La liste des clients à inserer est construite de manière decroissante du ratio.

    EN :
    For each client, we look for the place that minimises the increase of the cost of the objective function when it is
    inserted in the solution. The list of clients to be inserted is built in the decreasing order of the ratio
    """
    # 1 - Recherche des clients manquants
    listClientMissing = get_missing_client_list(solution.listTimeSlot, listClient)

    # Tri de la liste selon un critère de la méthode orderListOperator
    listClientMissing = methods.order_ListClient_by_ratio(listClientMissing)
    if not solution.listTimeSlot:
        # Ajout du time slot à la solution
        newTimeSlot = get_new_timeSlot(vehicle)
        solution.appendTimeSlot(newTimeSlot)
    solution.updateCost = True

    # Boucle de calcul du cout de la fonction objective si on met le client
    for client in listClientMissing:
        min_cost = 100000
        indice_best_timeslot, indice_best_route, indice_best_client = 0, 0, 0
        for timeSlot in range(len(solution.listTimeSlot)):
            min_cost, id_timeslot, id_route, id_client = best_insertion(solution, timeSlot, client, min_cost)
            if id_timeslot is not None:
                indice_best_timeslot = id_timeslot
                indice_best_route = id_route
                indice_best_client = id_client

        solution.listTimeSlot[indice_best_timeslot].listRoute[indice_best_route].insertClient(indice_best_client,
                                                                                              client)
