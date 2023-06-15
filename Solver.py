import methodes as md
import time


class Solver:
    def __init__(self, methode):
        self.methode = methode

    def preprocess(self, list_clients, list_collecteurs):
        selection = {}
        # for collecteur in list_collecteurs:
        #     selection[collecteur] = list_clients.copy()

        best_solution = []
        best_collecteur = None
        best_value = -1
        best_found_time = 0
        initial_time = time.perf_counter()

        # FOCAL POINT
        # focalPoint = md.leftmost_client(list_clients)
        # focalPoint = (focalPoint.location[0], focalPoint.location[1]-0.05)

        for step, collecteur in enumerate(list_collecteurs):
            # initialisation
            orderedList = list_clients.copy()  # verif avec deepcopy
            orderedList.sort(key=lambda x: (x.priorite(), x.capacite), reverse=True)
            selectedClient = []

            # on s'assure que le premier client ne dépasse pas la capacité du véhicule
            while orderedList and orderedList[0].quantite > collecteur.vehicule_capacite:
                orderedList.pop(0)
            # si aucun des clients ne peut être collecté par ce véhicule, alors on passe au suivant
            if not orderedList:
                continue

            # tant que le vehicule ne déborde pas on selectionne le client le plus prioritaire
            residualQuantity = collecteur.vehicule_capacite
            while residualQuantity >= 0 and orderedList:
                currentClient = orderedList.pop(0)
                selectedClient.append(currentClient)
                residualQuantity -= currentClient.quantite
            # suppression du client qui fait deborder le vehicule
            currentClient = selectedClient.pop()
            residualQuantity += currentClient.quantite
            orderedList.append(currentClient)

            current_solution = self.methode.solve(selectedClient, collecteur)
            found_time = time.perf_counter() - initial_time
            while not current_solution and selectedClient:
                # on supprime le point le plus loin
                indice = md.farthest_id_client(selectedClient, collecteur)
                selectedClient.pop(indice)
                # client = selectedClient.pop(indice)
                # client.request += 1  # pour plus tard

                current_solution = self.methode.solve(selectedClient, collecteur)
                found_time = time.perf_counter() - initial_time

            if not selectedClient:
                print("no client selected for {v} !!!!!!!!!!!!!!!".format(v=collecteur.nom))
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
            inside.sort(key=lambda x: (x.priorite(), x.capacite), reverse=True)
            tested_solution = []
            tested_found_time = 0
            while inside:
                first = inside.pop(0)
                if 0 <= residualQuantity - first.quantite:
                    selectedClient.append(first)
                    residualQuantity -= first.quantite

                    tested_solution = self.methode.solve(selectedClient, collecteur)
                    tested_found_time = time.perf_counter() - initial_time
                    if not tested_solution:
                        selectedClient.pop()
                        residualQuantity += first.quantite

            if not tested_solution:
                tested_solution = self.methode.solve(selectedClient, collecteur)
                tested_found_time = time.perf_counter() - initial_time

            tested_value = md.fitness(tested_solution, collecteur, list_clients)
            current_value = md.fitness(current_solution, collecteur, list_clients)

            if 0 < tested_value < current_value:
                print("bonus")
                current_solution = tested_solution.copy()
                current_value = tested_value
                found_time = tested_found_time

            if 0 < current_value < best_value or best_value == -1:
                best_solution = current_solution.copy()
                best_collecteur = collecteur
                best_value = current_value
                best_found_time = found_time

            print("End of vehicle routing {i} : {t}".format(i=step, t=time.perf_counter() - initial_time))

        print("Solution trouvé en {t} / {tt} s".format(t=round(best_found_time, 2),
                                                       tt=round(time.perf_counter() - initial_time, 2)))

        selection[best_collecteur] = best_solution
        return selection

    def solve(self, list_client, collecteur, showLog=False):
        return self.methode.solve(list_client, collecteur, showLog)
