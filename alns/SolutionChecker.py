def check_all_visited(listClient, clientToVisit, showLog=False):
    for client in listClient:
        if client in clientToVisit and not client.visite:
            if showLog:
                print("Solution non valide - Client {i} non visité".format(i=client.indice))

            # Réinitialisation complète de la liste avant de retourner False
            for clientVisited in listClient:
                clientVisited.visite = False
            return False
        elif client not in clientToVisit and client.visite:
            if showLog:
                print("Solution non valide - Client {i} visité".format(i=client.indice))

            # Réinitialisation complète de la liste avant de retourner False
            for clientVisited in listClient:
                clientVisited.visite = False
            return False
        else:
            # S'il a bien été visité et qu'il devait l'être on le réinitialise
            client.visite = False
    return True


def check(solution, clientToVisit=None, showLog=False, notSommetVisited=False):
    clientToVisit = solution.instance.listClient if clientToVisit is None else clientToVisit

    # Méthode permettant de vérifier que l'on satisfait toutes les contraintes du problème
    '''Contrainte du nombre de time slot utilisés'''
    if len(solution.listTimeSlot) > solution.numberTimeSlotMax:
        if showLog:
            print("Solution non valide - Nombre de time slots")
        return False

    for timeSlot in solution.listTimeSlot:
        # Si le time slot ne contient pas de routes
        if len(timeSlot.listRoute) == 0:
            # On peut le supprimer
            solution.removeTimeSlot(timeSlot)
            # On lance un check de la solution modifiée
            return check(solution, clientToVisit, showLog, notSommetVisited)

        '''Contrainte du nombre de routes par time slot'''
        if len(timeSlot.listRoute) > solution.routePerTimeSlotMax:
            if showLog:
                print("Solution non valide - Nombre de routes par time slot")
            return False

        for route in timeSlot.listRoute:
            # Si la route courante n'a que 2 clients, alors elle ne passe par aucun point de collecte
            # Elle fait 0 → 0
            size = len(route.trajet)
            if size <= 2:
                # On peut donc la supprimer
                timeSlot.removeRoute(route)
                # On lance un check de la solution modifiée
                return check(solution, clientToVisit, showLog, notSommetVisited)

            '''Contrainte de démarrer du dépôt'''
            if route.trajet[0].indice != route.collecteur.indice:
                if showLog:
                    print("Solution non valide - Début d'une route sans dépôt")
                return False

            '''Contrainte de capacité du véhicule'''
            if route.getTotalQuantity() > route.collecteur.vehicule_capacite:
                if showLog:
                    print("Solution non valide - Capacité max du véhicule")
                return False

            '''Contrainte de finir par le dépôt'''
            if route.trajet[-1].indice != route.collecteur.indice:
                if showLog:
                    print("Solution non valide - Fin d'une route sans dépôt")
                return False

            '''Contrainte des horaires'''
            if not route.canPass(solution.instance.getDistance):
                if showLog:
                    print("Solution non valide - Horaires non respectés")
                return False

            # Sauf si on spécifie de ne pas vérifier les sommets visités pour les opérateurs de réparation
            if not notSommetVisited:
                # Validation du passage par le sommet
                for client in route.trajet:
                    client.visite = True

        '''Contrainte de durée du time slot'''
        durationTimeSlot = timeSlot.getDuration(solution.instance.getDistance)
        if durationTimeSlot > solution.durationTimeSlotMax:
            if showLog:
                print("Solution non valide - Durée du time slot dépassée {v} > {u}"
                      .format(v=durationTimeSlot, u=solution.durationTimeSlotMax))
            return False

    # Sauf si on spécifie de ne pas vérifier les sommets visités pour les opérateurs de réparation
    if not notSommetVisited:
        return check_all_visited(solution.instance.listClient, clientToVisit, showLog)

    return True


def quick_check(solution, clientToVisit=None, showLog=False):
    clientToVisit = solution.instance.listClient if clientToVisit is None else clientToVisit

    for timeslot in solution.listTimeSlot:
        for route in timeslot.listRoute:
            if not route.canPass(solution.instance.getDistance):
                if showLog:
                    print("Solution non valide - Horaires non respectés")
                return False
            for client in route.trajet:
                client.visite = True

    return check_all_visited(solution.instance.listClient, clientToVisit, showLog)
