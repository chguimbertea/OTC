"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
import random


def get_one_random_client(solution):
    bound = max(0, len(solution.listTimeSlot) - 1)
    timeSlot = solution.listTimeSlot[random.randint(0, bound)]

    bound = max(0, len(timeSlot.listRoute) - 1)
    route = timeSlot.listRoute[random.randint(0, bound)]

    bound = max(1, len(route.trajet) - 2)
    position = random.randint(1, bound)
    return route.removeClientByPosition(position)


def destroy_random(solution, degree_destruction):
    """ RANDOM REMOVAL
    FR :
    Opérateur de destruction aléatoire d'un nombre de clients donné par le degré de destruction

    EN :
    Operator of random destruction of a number of clients given by the degree of destruction
    """
    # Calcul du nombre de clients à détruire
    nbClientToDestroy = degree_destruction

    nbIteration = 0
    # Boucle de destruction des clients
    while nbIteration < nbClientToDestroy:
        # Identification du client à détruire
        if len(solution.listTimeSlot) > 1:
            timeSlot = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]
        else:
            timeSlot = solution.listTimeSlot[0]

        if len(timeSlot.listRoute) > 1:
            route = timeSlot.listRoute[random.randint(0, len(timeSlot.listRoute) - 1)]
        else:
            route = timeSlot.listRoute[0]

        if len(route.trajet) >= 3:
            position = random.randint(1, len(route.trajet) - 2)

            # Destruction du client
            route.removeClientByPosition(position)

            # Incrémentation du compteur d'itérations
            nbIteration += 1


def destroy_Client_with_a_request_placed_at_the_end_of_the_solution(solution, degree_destruction, listClient):
    """ DESTROY CLIENT WITH A REQUEST
    FR :
    Opérateur de destruction basé sur le request des clients.
    Si le client est en fin de solution et qu'elle est requested alors on peut la supprimer

    EN :
    Destruction operator based on client request.
    If the client is at the end of the solution and it is requested then it can be deleted
    """
    # Calcul du nombre de clients à détruire
    nbClientRequested = 0

    for client in listClient:
        if client.isRequested():
            nbClientRequested += 1

    numberOfClientToDestroy = degree_destruction
    if nbClientRequested == 0:
        nbClientRequested = 1

    if nbClientRequested < degree_destruction:
        numberOfClientToDestroy = nbClientRequested

    # Initialisation des variables
    allClientDestroyed = False
    nbClientDestroyed = 0

    if len(solution.listTimeSlot) >= 2:
        for indiceTimeSlot in range(len(solution.listTimeSlot) - 1, 0, -1):
            timeSlot = solution.listTimeSlot[indiceTimeSlot]
            for route in timeSlot.getListRoute():
                for client in route.getTrajet():
                    if client.isRequested():
                        route.removeClient(client)
                        nbClientDestroyed += 1
                        if nbClientDestroyed >= numberOfClientToDestroy:
                            allClientDestroyed = True
                            break
                if allClientDestroyed:
                    break
            if allClientDestroyed:
                break


def destroy_Client_with_a_high_ratio_placed_at_the_end_of_the_solution(solution, degree_destruction):
    """ DESTROY CLIENT HIGH RATIO
    FR:
    Opérateur de destruction visant à détruire les clients ayant un ratio élevé en fin de solution
    Ratio = quantité / capacité (+1 si le client est requested)

    EN :
    Destruction operator to destroy customers with a high ratio at the end of the solution
    Ratio = quantity / capacity (+1 if the customer is requested)
    """
    # Initialisation des variables
    numberOfClientToDestroy = degree_destruction
    nbRouteDestroyed = 0
    ratioMax = 2

    # Tant qu'on n'a pas détruit tous les clients demandés on recommence
    while nbRouteDestroyed < numberOfClientToDestroy and ratioMax >= 0:
        clientDestroyed = False
        for indiceTimeSlot in range(len(solution.listTimeSlot) - 1, 0, -1):
            timeSlot = solution.listTimeSlot[indiceTimeSlot]
            for route in timeSlot.getListRoute():
                for indiceClient in range(1, len(route.trajet) - 1):
                    client = route.getClientByIndex(indiceClient)

                    # Calcul du ratio plus 1 s'il est requested
                    ratio = client.getRatio() + 1*client.isRequested()

                    # Si le ratio est supérieur à la borne max, alors on supprime le client
                    if ratio >= ratioMax:
                        # Suppression du client
                        route.removeClientByPosition(indiceClient)

                        # Update des variables de boucles
                        nbRouteDestroyed += 1
                        clientDestroyed = True

                        # Sort de la boucle de client
                        break
                # Sort de la boucle de route
                if clientDestroyed:
                    break
            # Sort de la boucle de time slot
            if clientDestroyed:
                break
        if not clientDestroyed:
            ratioMax -= 0.1


def destroy_worst_clients(solution, degree_destruction):
    """ WORST REMOVAL
    FR :
    destruction des clients les plus couteux dans l'objectif

    EN :
    destroy customers the most costly in the objective
    """
    nbClientToDestroy = degree_destruction
    nbIteration = 0

    # Boucle de destruction des clients
    while nbIteration < nbClientToDestroy:
        # for each client we initialize these variables
        gain = 0
        indice_worst_timeslot = 0
        indice_worst_route = 0
        indice_worst_client = -1

        for timeSlot in range(len(solution.listTimeSlot)):
            for route in range(len(solution.listTimeSlot[timeSlot].listRoute)):
                for indiceClient in range(1, len(solution.listTimeSlot[timeSlot].listRoute[route].trajet) - 1):
                    before = solution.getCost()
                    client = solution.listTimeSlot[timeSlot].listRoute[route].removeClientByPosition(indiceClient)
                    after = solution.getCost()
                    new_gain = before - after
                    #  the objective is to find the maximum "gain" for each client
                    if new_gain > gain or indice_worst_client == -1:
                        gain = new_gain
                        indice_worst_timeslot = timeSlot
                        indice_worst_route = route
                        indice_worst_client = indiceClient
                    solution.listTimeSlot[timeSlot].listRoute[route].insertClient(indiceClient, client)
        solution.listTimeSlot[indice_worst_timeslot].listRoute[indice_worst_route] \
            .removeClientByPosition(indice_worst_client)
        nbIteration += 1


def destroy_related_client_by_distance(solution, degree_destruction, listClient):
    """ RELATED REMOVAL with alpha = 1, beta = 0, gamma = 0
    FR :
    mesure de la relativite entre clients qui correspond aux distances/temps.

    EN :
    measure of relativity between customers in terms of distance between customers
    """
    destroy_related_clients(solution, degree_destruction, listClient, alpha=1, beta=0, gamma=0)


def destroy_related_clients(solution, degree_destruction, listClient, alpha=0.5, beta=0.25, gamma=0.25):
    """ RELATED REMOVAL with alpha < 1 OR beta != 0 OR gamma != 0
    FR :
    mesure de la relativite entre clients qui correspond a une ponderation entre distance, ratio et request
    à chaque étape un client est choisi et on enlève son plus proche voisin.

    EN :
    measure of relativity between clients that corresponds to a weighting between distance, ratio and request
    at each step, we choose a client and remove its nearest neighbor.
    """
    # Destruction aleatoire du premier client
    first_client = get_one_random_client(solution)
    removed_clients = [first_client]

    nbIteration = 0
    nbClientToDestroy = degree_destruction

    liste = [p for p in listClient]

    while nbIteration < nbClientToDestroy - 1:
        choosed_client = random.choices(removed_clients)[0]
        client_plus_proche = 0
        Related_min = 200
        for client in liste:  # taille de la matrice des distances
            if client not in removed_clients:
                dist = solution.instance.getDistance(choosed_client.getIndice(), client.getIndice())
                delta = abs(int(choosed_client.request) - int(client.request))
                ratio = abs((choosed_client.getRatio()) - (client.getRatio()))
                Related = alpha * dist + beta * delta + gamma * ratio
                if Related < Related_min:
                    Related_min = Related
                    client_plus_proche = client
        removed_clients.append(client_plus_proche)

        for timeslot in solution.getListTimeSlot():
            for route in timeslot.getListRoute():
                for client in route.getTrajet():
                    if client.getIndice() == client_plus_proche.getIndice():
                        route.removeClient(client)
        nbIteration += 1


def destroy_route(solution):
    """ DESTROY ROUTE
    FR :
    Detruit une route aleatoire dans la solution. Le nb de clients detruits ne depend pas du degrès de destruction
    mais du nombre de clients de la route detruite.

    EN :
    Destroys a random route in the solution. The number of customers destroyed does not depend on the degree of
    destruction but on the number of customers on the destroyed route.
    """
    timeSlot = solution.listTimeSlot[random.randint(0, len(solution.listTimeSlot) - 1)]
    route = timeSlot.listRoute[random.randint(0, len(timeSlot.listRoute) - 1)]

    route.trajet = [route.vehicle.depot, route.vehicle.depot]
    route.totalQuantity = 0
    route.duration = 0
