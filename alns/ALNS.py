"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from alns.TimeSlot import TimeSlot
from alns.Route import Route
from alns.Solution import Solution
import alns.methods as methods
import alns.destroyMethods as destroyMethods
import alns.repairsMethods as repairsMethods
from alns.SolutionChecker import check

import time
import random
import copy
import math
import matplotlib.pyplot as plt


class ALNS:
    bound = 1000

    def __init__(self, instance, numberTimeSlotMax=1, routePerTimeSlotMax=None, durationTimeSlotMax=420,
                 listClient=None, vehicle=None):
        # Initialisation de l'instance
        self.instance = instance
        self.listClient = instance.listClient if listClient is None else listClient
        self.vehicle = instance.vehicle if vehicle is None else vehicle

        self.numberTimeSlotMax = numberTimeSlotMax
        self.routePerTimeSlotMax = len(self.listClient) if routePerTimeSlotMax is None else routePerTimeSlotMax
        self.durationTimeSlotMax = durationTimeSlotMax
        self.nIter = (len(self.listClient) - 1) / 2 * 1000

        # Initialisation de la solution finale
        self.bestSolution = Solution(self.instance, self.numberTimeSlotMax, self.routePerTimeSlotMax,
                                     self.durationTimeSlotMax)

        # fréquence d'affichage des logs de recherche
        self.displayFrequency = 500

        # nombre de fois où on accepte une solution moins bonne
        self.onremontelapente = 0

        # nombre de fois où les repair ne marchent pas et on repart de la solution gardée en mémoire
        self.repairdontwork = {}

        # Listes des noms des méthodes de destruction
        # "destroy_route",
        # "destroy_random",
        # "destroy_worst_clients",
        # "destroy_related_clients", (alpha, beta, gamma)
        # "destroy_related_client_by_distance",
        # "destroy_Client_with_a_request_placed_at_the_end_of_the_solution",
        # "destroy_Client_with_a_high_ratio_placed_at_the_end_of_the_solution"
        self.destroy_methods = ["destroy_route",
                                "destroy_random",
                                "destroy_worst_clients",
                                "destroy_Client_with_a_high_ratio_placed_at_the_end_of_the_solution",
                                "destroy_Client_with_a_request_placed_at_the_end_of_the_solution"]

        # Listes des noms des méthodes de repair
        # "repair_randomV2",
        # "repair_randomv1",
        # "repair_2_regret",
        # "repair_random_best_insertion",
        # "repair_max_ratio_best_insertion",
        # "repair_FirstPositionAvailable_randomlistClient",
        # "repair_FirstPositionAvailable_maxratio_listClient"
        self.repair_methods = ["repair_2_regret",
                               "repair_randomv1",
                               "repair_random_best_insertion",
                               "repair_max_ratio_best_insertion",
                               "repair_FirstPositionAvailable_maxratio_listClient"]

        self.repairdontwork = {}
        self.weights_destroy = {}
        self.weights_repair = {}
        self.USED_METHODS = {}
        self.USED_METHODS_UNTIL_LAST_BEST = {}
        self.sucess_swap = {}
        self.evolution_iter_best = None
        self.evolution_time_best = None
        self.evolution_cost = None

    def getSolution(self):
        return self.bestSolution

    def setListClient(self, listClient):
        # attention si client n'est pas dans l'instance !!
        self.listClient = listClient

    def setVehicle(self, vehicle):
        self.vehicle = vehicle

    def createTimeSlot(self, listClient):
        timeSlot = TimeSlot()

        # Boolean indiquant lorsqu'aucun client ne peut être ajouté sans violer la contrainte de durée
        moreClientForDuration = True

        # Tant que la durée du time slot n'est pas dépassée et que le nombre de routes est inférieur à la limite
        while (timeSlot.getDuration(self.instance.getDistance) <= self.durationTimeSlotMax
               and len(timeSlot.listRoute) < self.routePerTimeSlotMax
               and moreClientForDuration):

            # Initialisation pour vérifier si un client a été ajouté
            moreClientForDuration = False

            # Création de la route
            route = Route(self.vehicle)
            timeSlot.appendRoute(route)

            # Boolean indiquant lorsqu'aucun client ne peut être ajouté sans violer la contrainte de capacité
            moreClientForCapacity = True

            # Tant que la capacité du véhicule n'est pas atteinte
            while route.getTotalQuantity() <= route.vehicle.capacity and moreClientForCapacity:

                # Initialisation pour vérifier si un client a été ajouté
                moreClientForCapacity = False

                # Boucle sur les clients de l'instance
                for client in listClient:
                    # S'il est non visité, on l'ajoute
                    if not client.isVisited() and client.indice < 1000:
                        route.insertClient(-1, client)

                        # Vérification des contraintes de durée du time slot, de capacité du véhicule et d'horaires
                        if timeSlot.getDuration(self.instance.getDistance) <= self.durationTimeSlotMax \
                                and route.getTotalQuantity() <= route.vehicle.capacity \
                                and route.canPass(self.instance.getDistance):
                            # Si oui alors on valide l'ajout
                            client.setVisited()
                            moreClientForCapacity = True
                            moreClientForDuration = True

                        else:
                            # Sinon, on supprime l'ajout
                            route.removeClientByPosition(-2)

        return timeSlot

    def createSolution(self):
        """
        FR :
        Méthode de création d'une solution basique
        Ajout de client dans une route dans leur ordre de parsing jusqu'à atteindre
        soit la capacité max du véhicule soit la durée max du time slot
        Une fois la capacité atteinte on essaie d'ajouter une autre route au time slot
        Sinon on crée un autre time slot

        EN :
        Method of creating a basic solution
        Adding clients in a route in their parsing order until reaching either the max capacity of the vehicle
        or the maximum duration of the time slot
        Once the capacity is reached, we try to add another route to the time slot
        Otherwise we create another time slot
        """
        # Initialisation des variables
        listClient = methods.order_ListClient_random(self.listClient.copy())
        clientNotPlaced = True

        # Réinitialisation de la currentSolution
        solution = Solution(self.instance, self.numberTimeSlotMax, self.routePerTimeSlotMax, self.durationTimeSlotMax)

        while clientNotPlaced and len(solution.listTimeSlot) < self.numberTimeSlotMax:
            # Si tous les clients sont placés alors on met fin à la boucle
            clientNotPlaced = False

            # Création du timeSlot
            timeSlot = self.createTimeSlot(listClient)

            # Ajout du timeSlot à la solution en cours
            solution.appendTimeSlot(timeSlot)

            # Vérification que tous les clients ont été visités
            for client in self.listClient:
                if not client.isVisited():
                    clientNotPlaced = True
                    break

        # Réinitialisation des visites des clients
        for client in self.listClient:
            client.setNotVisited()

        return solution

    def modification(self, solution, keptinmemory, destroy_method, degree_destruction, repair_method):
        """
        FR:
        Fonction prenant la solution courante et la transforme suivant la méthode de destruction et la méthode
        de repair choisies. Cette fonction modifie current_solution. La nouvelle solution est dans current_solution.

        EN :
        Function taking the current solution and transforming it according to the chosen destruction method and
        repair method. This function modifies current_solution. The new solution is in current_solution.
        """
        if destroy_method == "destroy_worst_clients":
            destroyMethods.destroy_worst_clients(solution, degree_destruction)
        if destroy_method == "destroy_random":
            destroyMethods.destroy_random(solution, degree_destruction)
        if destroy_method == "destroy_related_client_by_distance":
            destroyMethods.destroy_related_client_by_distance(solution, degree_destruction, self.listClient)
        if destroy_method == "destroy_related_clients":
            destroyMethods.destroy_related_clients(solution, degree_destruction, self.listClient)
        if destroy_method == "destroy_Client_with_a_high_ratio_placed_at_the_end_of_the_solution":
            destroyMethods.destroy_Client_with_a_high_ratio_placed_at_the_end_of_the_solution(solution,
                                                                                              degree_destruction)
        if destroy_method == "destroy_Client_with_a_request_placed_at_the_end_of_the_solution":
            destroyMethods.destroy_Client_with_a_request_placed_at_the_end_of_the_solution(solution, degree_destruction,
                                                                                           self.listClient)
        if destroy_method == "destroy_route":
            destroyMethods.destroy_route(solution)

        if repair_method == "repair_2_regret":
            repairsMethods.repair_2_regret(solution, self.listClient, self.vehicle)
        if repair_method == "repair_max_ratio_best_insertion":
            repairsMethods.repair_max_ratio_best_insertion(solution, self.listClient, self.vehicle)
        if repair_method == "repair_FirstPositionAvailable_randomlistClient":
            repairsMethods.repair_FirstPositionAvailable_randomlistClient(solution, self.listClient, self.vehicle,
                                                                          self.numberTimeSlotMax,
                                                                          self.routePerTimeSlotMax, self.repairdontwork)
        if repair_method == "repair_randomv1":
            repairsMethods.repair_randomv1(solution, self.listClient, self.vehicle, self.repairdontwork)
        if repair_method == "repair_randomV2":
            repairsMethods.repair_randomV2(solution, self.listClient, self.vehicle, self.numberTimeSlotMax,
                                           self.routePerTimeSlotMax, self.repairdontwork)
        if repair_method == "repair_FirstPositionAvailable_maxratio_listClient":
            repairsMethods.repair_FirstPositionAvailable_maxratio_listClient(solution, self.listClient, self.vehicle,
                                                                             self.numberTimeSlotMax,
                                                                             self.routePerTimeSlotMax,
                                                                             self.repairdontwork)
        if repair_method == "repair_random_best_insertion":
            repairsMethods.repair_random_best_insertion(solution, self.listClient, self.vehicle, self.numberTimeSlotMax,
                                                        self.routePerTimeSlotMax)

        # Calcul du coût de la solution à mettre à jour
        if not check(solution, self.listClient):
            solution.clone(keptinmemory)
        else:
            self.repairdontwork[repair_method] += 1
            keptinmemory.clone(solution)

    def init_solution(self):
        cpt = 0
        while cpt < ALNS.bound:
            solution = self.createSolution()
            if check(solution, self.listClient):
                return solution
            cpt += 1
        return Solution(self.instance, self.numberTimeSlotMax, self.routePerTimeSlotMax, self.durationTimeSlotMax)

    def solve(self, pu=100, rho=0.3, sigma1=135, sigma2=70, sigma3=25, tolerance=0.05, coolingRate=0.99975, nc=2000,
              dMax=0.2, theta=0.5, nbSwap=10, withSwap=False, showLog=False):
        """
        FR:
        Fonction principale. Les différentes parties sont représentées dans le logigramme ou le pseudo code du rapport.
        Cette fonction a en argument tous les paramètres de l'algorithme et retourne la meilleure solution.
        currentSolution correspond à la solution que l'on modifie à chaque iteration.
        testSolution correspond à la solution gardée en mémoire à laquelle on va comparer current solution.

        EN :
        Main function.The different parts are represented in the flowchart or the pseudo code of the report.
        This function has as argument all the parameters of the algorithm and returns the best solution.
        currentSolution corresponds to the solution that we modify at each iteration.
        testSolution corresponds to the solution kept in memory to which we will compare current solution.
        """
        if showLog:
            print("Solving " + self.instance.name)
        if not methods.fast_check(self.listClient, self.numberTimeSlotMax, self.routePerTimeSlotMax,
                                  self.durationTimeSlotMax):
            return Solution(self.instance, self.numberTimeSlotMax, self.routePerTimeSlotMax, self.durationTimeSlotMax)

        # INITIALISATION DU TEMPS
        initialTime = time.perf_counter()

        # INITIALISATION DES SOLUTIONS
        self.bestSolution = self.init_solution()
        if not self.bestSolution.listTimeSlot:
            if showLog:
                print("Too many tries, invalid solution")
            return self.bestSolution

        testSolution = self.bestSolution.copy()
        currentSolution = self.bestSolution.copy()

        # INITIALISATION DES VARIABLES
        T0 = (tolerance * self.bestSolution.getCost()) / math.log(2)  # temperature initiale
        nbIteration = 0  # nombre d'itérations
        iterationMaxSinceLastBest = nc  # nombre d'itérations maximum avant de réinitialiser la solution
        nbIterationSinceLastBest = 0  # nombre d'itérations avant de réinitialiser la solution
        self.onremontelapente = 0  # nombre de fois que l'on accepte une solution moins bonne
        self.evolution_iter_best = [nbIteration]  # iterations où on améliore la meilleure solution
        self.evolution_time_best = [nbIteration]  # temps où on améliore la meilleure solution
        self.evolution_cost = [round(self.bestSolution.getCost(), 2)]  # évolution du cout de la meilleure solution

        self.repairdontwork = {i: 0 for i in self.repair_methods}

        # INITIALISATION DES POIDS POUR LA "ROULETTE WHEEL SELECTION"
        # initialement même poids pour toutes les méthodes
        self.weights_destroy = {i: 1 / len(self.destroy_methods) for i in self.destroy_methods}
        self.weights_repair = {i: 1 / len(self.repair_methods) for i in self.repair_methods}

        Success_destroy = {i: 0 for i in self.destroy_methods}
        Used_destroy_methods = {i: 0 for i in self.destroy_methods}

        Success_repair = {i: 0 for i in self.repair_methods}
        Used_repair_methods = {i: 0 for i in self.repair_methods}

        # dictionnaires avec pour clé le nom de la methode et
        # pour valeur le nombre de fois que l'on utilise une methode en s'arrêtant à la dernière meilleure solution
        self.USED_METHODS = {i: 0 for i in self.destroy_methods + self.repair_methods}
        self.USED_METHODS_UNTIL_LAST_BEST = {}

        self.sucess_swap = {'swap_inter_route': 0, 'swap_intra_route': 0}

        # Headers de l'affichage de recherche de solution
        if showLog:
            print("Nb iteration", "Clock", "Best solution", "Nb de solutions moins bonnes acceptées", sep='\t')

        # CRITÈRE D'ARRÊT : nIter iterations maximum :
        while nbIteration < self.nIter:
            # VÉRIFICATION DE L'AMÉLIORATION DE LA SOLUTION
            if nbIterationSinceLastBest >= iterationMaxSinceLastBest:
                # Si on n'améliore pas la best solution, alors on recommence en cherchant avec
                # une nouvelle solution de départ en mélangeant la liste de création de la solution

                # Réinitialisation du compteur
                nbIterationSinceLastBest = 0

                # Création d'une nouvelle solution de départ
                currentSolution = self.init_solution()
                if not currentSolution.listTimeSlot:
                    if showLog:
                        print("Too many tries, invalid solution for reset")
                    return self.bestSolution
                else:
                    # Mise à jour de la solution de test
                    testSolution.clone(currentSolution)

            # CHOIX D'UN OPÉRATEUR DE DESTRUCTION
            # 0.2 : Degré de destruction faible pour détruire peu → améliore le temps de calcul
            # 0.4 : Degré de destruction fort pour détruire plus de clients
            #        → allonge le temps de calcul,pu mais diversifie les solutions
            degree_destruction = random.randint(math.ceil(0.1 * len(self.listClient)),
                                                math.ceil(dMax * len(self.listClient)))

            destroy_method = methods.choose_destroy_method(self.destroy_methods, self.weights_destroy)

            Used_destroy_methods[destroy_method] += 1
            self.USED_METHODS[destroy_method] += 1

            # CHOIX D'UN OPÉRATEUR DE RECONSTRUCTION
            repair_method = methods.choose_repair_method(self.repair_methods, self.weights_repair)

            Used_repair_methods[repair_method] += 1
            self.USED_METHODS[repair_method] += 1

            # MODIFICATION DE LA SOLUTION
            # on sauvegarde en memoire la solution courante pour pouvoir repartir de cette solution
            keptinmemory = currentSolution.copy()
            # on sauvegarde en memoire la meilleure solution courante pour pouvoir repartir de cette solution
            # keptinmemory = self.bestSolution.copy()

            self.modification(currentSolution, keptinmemory, destroy_method, degree_destruction, repair_method)

            # ATTEINT-ON LA CONDITION POUR FAIRE LES SWAPS ?
            if withSwap and currentSolution.getCost() < (1 + theta) * testSolution.getCost():
                # ON REALISE Ns SWAPS DE CHAQUE TYPE : 'swap_inter_route' & 'swap_intra_route'
                for k in range(nbSwap):
                    # SWAP de deux clients au sein d'une route
                    methods.swap_inter_route(currentSolution, self.listClient)

                    # si le swap améliore la solution, on la garde en memoire
                    if currentSolution.getCost() < keptinmemory.getCost():
                        keptinmemory.clone(currentSolution)
                        self.sucess_swap['swap_inter_route'] += 1

                    # SWAP de deux clients au hasard dans la solution
                    methods.swap_intra_route(currentSolution, self.listClient)

                    # si le swap détériore la solution, on repart de celle juste avant
                    if currentSolution.getCost() > keptinmemory.getCost():
                        currentSolution.clone(keptinmemory)
                    # si le swap améliore la solution, on la garde en memoire
                    else:
                        keptinmemory.clone(currentSolution)
                        self.sucess_swap['swap_intra_route'] += 1

            # CRITÈRE D'ACCEPTATION
            # methods.acceptance_criteria_simulated_annealing(T0,alpha,nbIteration)
            # methods.acceptance_criteria_greedy(currentSolution, testSolution)

            if methods.acceptance_criteria_simulated_annealing(currentSolution, testSolution, T0, coolingRate,
                                                               nbIteration,
                                                               self.onremontelapente):
                # la solution courante est acceptée par le critère d'acceptance donc on la sauvegarde
                testSolution.clone(currentSolution)

                if currentSolution.getCost() < self.bestSolution.getCost():
                    # si on a une meilleure solution, on met à jour testSolution et bestSolution
                    # et on récompense les méthodes qui ont réussi par la quantité sigma1
                    self.bestSolution.clone(currentSolution)
                    Success_destroy[destroy_method] += sigma1
                    Success_repair[repair_method] += sigma1

                    # mise à jour des variables d'informations
                    self.evolution_cost.append(round(self.bestSolution.getCost(), 2))
                    self.evolution_time_best.append(round(time.perf_counter() - initialTime, 3))
                    self.USED_METHODS_UNTIL_LAST_BEST = copy.deepcopy(self.USED_METHODS)
                    nbIterationSinceLastBest = 0
                    self.evolution_iter_best.append(nbIteration + 1)

                elif currentSolution.getCost() <= testSolution.getCost():
                    # et on récompense les méthodes qui ont réussi par la quantité sigma2
                    Success_destroy[destroy_method] += sigma2
                    Success_repair[repair_method] += sigma2

                else:
                    # on met à jour la solution en mémoire et on récompense les méthodes par la quantité sigma3
                    Success_destroy[destroy_method] += sigma3
                    Success_repair[repair_method] += sigma3

            # mise à jour du nombre d'itérations
            nbIteration += 1
            nbIterationSinceLastBest += 1

            # Si on a atteint Pu itérations → changements des probabilités associées à chaque méthode
            if nbIteration % pu == 0:
                self.weights_destroy, self.weights_repair = methods.update_weights(rho, self.weights_destroy,
                                                                                   self.weights_repair, Success_destroy,
                                                                                   Success_repair, Used_destroy_methods,
                                                                                   Used_repair_methods)

                Success_destroy = {i: 0 for i in self.destroy_methods}
                Success_repair = {i: 0 for i in self.repair_methods}

                Used_destroy_methods = {i: 0 for i in self.destroy_methods}
                Used_repair_methods = {i: 0 for i in self.repair_methods}

            if showLog and nbIteration % self.displayFrequency == 0:
                print("{nIter}\t\t{time}\t{cost}\t\t{nbr}".format(nIter=nbIteration,
                                                                  time=round(time.perf_counter() - initialTime, 2),
                                                                  cost=round(self.bestSolution.getCost(), 2),
                                                                  nbr=self.onremontelapente))
                self.onremontelapente = 0

        self.bestSolution.setTime(self.evolution_time_best[-1], round(time.perf_counter() - initialTime, 3))
        self.bestSolution.setParameters(self.nIter, pu, rho, sigma1, sigma2, sigma3, tolerance, coolingRate, nc, theta,
                                        nbSwap)

        if showLog:
            print("Cost = {cost}".format(cost=self.bestSolution.cost()))
            print("Time = {time}/{total}".format(time=self.bestSolution.foundTime, total=self.bestSolution.totalTime))
            print("fitness = {f}".format(f=self.bestSolution.fitness()))
            # self.display()
            print("#####")
            plt.plot(self.evolution_iter_best, self.evolution_cost)
            plt.ylabel('cost')
            plt.show()

        return self.bestSolution

    def display(self):
        print("## Nombre de fois ou les repair ne marchent pas et on repart de la solution gardée en memoire :")
        print(self.repairdontwork)
        print("## Iterations où on améliore la meilleure solution :")
        print(self.evolution_iter_best)
        print("## Temps où on améliore la meilleure solution :")
        print(self.evolution_time_best)
        print("## Evolution du cout de la meilleure solution :")
        print(self.evolution_cost)
        print("## Utilisation des méthodes jusqu'a la dernière meilleure solution :")
        print(self.USED_METHODS_UNTIL_LAST_BEST)
        print("## Utilisation des méthodes :")
        print(self.USED_METHODS)
        print("## Poids des méthodes de destructions :")
        print(self.weights_destroy)
        print("## Poids des méthodes de repair :")
        print(self.weights_repair)
        print("## Succès des swaps")
        print(self.sucess_swap)
        print("### BEST SOLUTION :")
        self.bestSolution.display()
