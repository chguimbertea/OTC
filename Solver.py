import methodes as md
import time

from preview import previewConvexHull


def print_select(select):
    result = {}
    for key, values in select.items():
        liste = []
        for v in values:
            liste.append(v.indice)
        result[key.nom] = liste
    print(result)


def stop_selection(clients, niv_priorite=0.9):
    for client in clients:
        if client.priorite() > niv_priorite:
            return False
    return True


class Solver:
    def __init__(self, methode):
        self.methode = methode
        self.showLog = False

    # FONTIONS POUR LA PREMIÈRE MÉTHODE DE SÉLECTION

    def semi_selection(self, list_clients, list_collecteurs, selection, clients):
        best_solution = []
        best_collecteur = None
        best_value = -1

        # FOCAL POINT
        # focalPoint = md.leftmost_client(list_clients)
        # focalPoint = (focalPoint.location[0], focalPoint.location[1]-0.05)

        # verif !!!
        for key in selection.keys():
            for client in selection[key]:
                if client in list_clients:
                    print("remove", client.nom)
                    list_clients.remove(client)

        for step, collecteur in enumerate(list_collecteurs):
            # INITIALISATION
            initial_time = time.perf_counter()
            orderedList = list_clients.copy()  # verif avec deepcopy !!
            selectedClient = selection[collecteur] if collecteur in selection.keys() else []

            # on s'assure que le premier client ne dépasse pas la capacité du véhicule
            while orderedList and orderedList[0].quantite > collecteur.vehicule_capacite:
                orderedList.pop(0)
            # si aucun des clients ne peut être collecté par ce véhicule, alors on passe au suivant
            if not orderedList:
                continue

            # tant que le véhicule ne déborde pas, on sélectionne le client le plus prioritaire
            residualQuantity = collecteur.vehicule_capacite
            while residualQuantity >= 0 and orderedList:
                currentClient = orderedList.pop(0)
                selectedClient.append(currentClient)
                residualQuantity -= currentClient.quantite
            # suppression du client qui fait déborder le véhicule
            currentClient = selectedClient.pop()
            residualQuantity += currentClient.quantite
            orderedList.append(currentClient)

            current_solution = self.methode.solve(selectedClient, collecteur)
            while not current_solution and selectedClient:
                # on supprime le point le plus loin
                client = md.remove_farthest_client(selectedClient, collecteur)
                # client.request += 1  # pour plus tard

                current_solution = self.methode.solve(selectedClient, collecteur)

            if not selectedClient:
                print("No client selected for {v} !!!".format(v=collecteur.nom))
                continue

            # RECHERCHE DE POINTS SUPPLÉMENTAIRES POTENTIELS
            # SOIT À L'INTÉRIEUR DE L'ENVELOPPE CONVEXE
            # hullPoint = md.convexHull(selectedClient.copy(), collecteur.vehicule_type)
            # inside = md.inside_intersection(orderedList.copy(), hullPoint, focalPoint, residualQuantity)
            # SOIT PROCHE D'UN SEGMENT DE ROUTE
            inside = md.inside_near_points(orderedList.copy(), current_solution, residualQuantity)
            # previewConvexHull(selectedClient, listAllClient=instance.listClient,
            #                   filename="view_{i}".format(i=cpt), showLog=True)

            # tant que solution valide, on ajoute des points interieurs
            tested_solution = []
            while inside:
                first = inside.pop(0)
                if 0 <= residualQuantity - first.quantite:
                    selectedClient.append(first)
                    residualQuantity -= first.quantite

                    tested_solution = self.methode.solve(selectedClient, collecteur)
                    if not tested_solution:
                        selectedClient.pop()
                        residualQuantity += first.quantite

            if not tested_solution:
                tested_solution = self.methode.solve(selectedClient, collecteur)

            tested_value = md.fitness_single_routing(tested_solution, collecteur, clients)
            current_value = md.fitness_single_routing(current_solution, collecteur, clients)

            if 0 < tested_value < current_value:
                print("bonus")
                current_solution = tested_solution.copy()
                current_value = tested_value

            if 0 < current_value < best_value or best_value == -1:
                best_solution = current_solution.copy()
                best_collecteur = collecteur
                best_value = current_value

            print("Temps pour le collecteur n°{i} : {t}".format(i=step, t=time.perf_counter() - initial_time))
        return best_collecteur, best_solution

    def selection_meilleure_route(self, list_clients, list_collecteurs):
        clients_dispo = list_clients.copy()
        clients_dispo.sort(key=lambda x: (x.priorite()), reverse=True)

        selection = {}
        best_collecteur, best_solution = self.semi_selection(clients_dispo, list_collecteurs.copy(), selection, list_clients)
        selection[best_collecteur] = best_solution

        return selection


    def selection_routes_fct_proximite(self, list_clients, list_collecteurs, niv_priorite=0.9):
        list_clients.sort(key=lambda x: (x.priorite()), reverse=True)
        clients_dispo = list_clients.copy()
        collecteurs_dispo = list_collecteurs.copy()

        selection = {}
        for collecteur in list_collecteurs:
            selection[collecteur] = []

        for client in list_clients:
            if client.priorite() < niv_priorite:
                break
            collecteur = md.nearest_point(client, collecteurs_dispo)
            while collecteur.vehicule_capacite < client.quantite:
                if not collecteurs_dispo:
                    print("Aucun collecteur n'est assez grand pour collecter", client.nom)
                    return {}
                collecteurs_dispo.remove(collecteur)
                collecteur = md.nearest_point(client, collecteurs_dispo)
            selection[collecteur].append(client)
            clients_dispo.remove(client)

        # tant qu'il y a des points qui ont besoin d'être collecté avant 7 jours
        while not stop_selection(clients_dispo, niv_priorite):
            best_collecteur, best_solution = self.semi_selection(clients_dispo, collecteurs_dispo, selection, list_clients)
            selection[best_collecteur] = best_solution
            # retirer les points déjà sélectionnés
            for client in best_solution:
                if client in clients_dispo:  # vérification dans quel cas !!
                    clients_dispo.remove(client)

        return selection

    # FONTIONS POUR LA SECONDE MÉTHODE DE SÉLECTION : NON FONCTIONNELLES

    def get_points(self, points, plus, collecteur):
        result = self.methode.solve(points + [plus], collecteur)
        if len(result) > 2:
            result = result[1:-1]
        return result

    def etape(self, solution_courante, clients_dispo, collecteurs_dispo, best_value, niv):
        # if not clients_dispo or # distance max dépasser alors couper!!
        if not clients_dispo:
            return solution_courante

        pdc = clients_dispo.pop(0)
        if pdc.priorite() < 0.15:
            return solution_courante

        best_fils = self.etape(solution_courante, clients_dispo.copy(), collecteurs_dispo.copy(), best_value, niv + 1)
        fit_best_fils = md.fitness_multiple_routing(best_fils, self.list_clients)
        if self.showLog:
            print("fitness du fils n°", niv, " :", fit_best_fils)
            print_select(best_fils)

        for collecteur in collecteurs_dispo:
            solution_suivante = solution_courante.copy()

            if collecteur in solution_suivante.keys():
                if collecteur.nom not in pdc.collecteurs_disponibles:
                    continue
                # ordonner les points avec self.methode.solve()
                selection = self.get_points(solution_suivante[collecteur], pdc, collecteur)
                if not selection:
                    #print("no sol")
                    #print(print_select(solution_suivante), pdc.indice, collecteur.indice)
                    # à vérifie pourquoi !!!!!
                    continue
                solution_suivante[collecteur] = selection
            # si priorité inférieur à 0.15 alors plus de nouveau collecteur
            elif pdc.priorite() < 0.15:
                #print("fiiiiiiiiiiiiiiiin")
                collecteurs_dispo = list(solution_suivante.keys())
                continue
            else:
                solution_suivante[collecteur] = [pdc]

            fils = self.etape(solution_suivante, clients_dispo.copy(), collecteurs_dispo.copy(), best_value, niv + 1)
            fit = md.fitness_multiple_routing(fils, self.list_clients)
            if self.showLog:
                print("fitness du fils n°", niv, " :", fit)
                print_select(fils)

            if fit < fit_best_fils:
                best_fils = fils
                fit_best_fils = fit

        return best_fils

    def selection_branch_and_bound(self, list_clients, list_collecteurs):
        self.list_clients = list_clients
        clients_ordonnes = list_clients.copy()  # verif avec deepcopy !!
        clients_ordonnes.sort(key=lambda x: (x.priorite(), x.capacite), reverse=True)


        racine = {}
        fitness = md.fitness_multiple_routing(racine, list_clients)
        print("fitness de la racine :", fitness)

        if not list_clients or not list_collecteurs:
            return racine

        best_fitness = 999999999999
        niv = 1

        pdc = clients_ordonnes.pop(0)
        best_fils = self.etape(racine, clients_ordonnes.copy(), list_collecteurs.copy(), best_fitness, niv + 1)
        fit_best_fils = md.fitness_multiple_routing(best_fils, list_clients)
        if self.showLog:
            print("fitness du fils n°", niv, " :", fit_best_fils)
            print_select(best_fils)

        for collecteur in list_collecteurs:
            # si priorité inférieur à 0.15 alors plus de nouveau collecteur
            if pdc.priorite() < 0.15:
                print("fiiiiiiiiiin")
            if collecteur.nom not in pdc.collecteurs_disponibles:
                continue
            solution_suivante = {collecteur: [pdc]}
            fils = self.etape(solution_suivante, clients_ordonnes.copy(), list_collecteurs.copy(), best_fitness,
                              niv + 1)
            fit = md.fitness_multiple_routing(fils, list_clients)
            if self.showLog:
                print("fitness du fils n°", niv, " :", fit)
                print_select(fils)

            if fit < fit_best_fils:
                best_fils = fils
                fit_best_fils = fit

        return best_fils

    def preprocess(self, list_clients, list_collecteurs):
        # PREMIERE MÉTHODE DE SÉLECTION
        # elle permet de sélectionner les points à visiter sur une route, donc un collecteur,
        # de sorte à minimiser les insatisfactions des clients et minimiser l'utilisation du véhicule
        return self.selection_meilleure_route(list_clients, list_collecteurs)
        # tentative de sélectionner plusieurs routes de manière itérative
        # tant que tous les points supérieurs au niveau de priorité ne sont pas sélectionnés
        # return self.selection_routes_fct_proximite(list_clients, list_collecteurs, 0.9)

        # SECONDE MÉTHODE DE SÉLECTION : NON FONCTIONNELLE
        # tentative de sélectionner le meilleur ensemble de route (1 collecteur et des clients)
        # en utilisant une recherche en branch-and-bound
        # return self.selection_branch_and_bound(list_clients, list_collecteurs)

    def solve(self, list_client, collecteur, showLog=False):
        return self.methode.solve(list_client, collecteur, showLog)