"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from alns.TimeSlot import TimeSlot
import math


class Solution:
    facteurZ1 = 1
    facteurZ2 = 10
    facteurZ3 = 10
    facteurZ4 = 1

    def __init__(self, instance, ntm=-1, rpt=-1, dtm=-1):
        self.instance = instance
        self.listTimeSlot = []

        # Objective function
        self.duration = -1  # Z1
        self.requestPriorityPenalty = -1  # Z2
        self.inventoryPriorityPenalty = -1  # Z3
        # Z4 = len(self.listTimeSlot)

        # Fitness function
        self.satisfaction = 0
        self.fillRate = 0
        self.usingCost = 0

        # Execution time
        self.foundTime = -1
        self.totalTime = -1

        # ALNS parameters
        self.numberTimeSlotMax = ntm
        self.routePerTimeSlotMax = rpt
        self.durationTimeSlotMax = dtm
        self.nIter = -1
        self.pu = -1
        self.rho = -1
        self.sigma1 = -1
        self.sigma2 = -1
        self.sigma3 = -1
        self.tau = -1
        self.c = -1
        self.nc = -1
        self.theta = -1
        self.ns = -1

    def setTime(self, foundTime, totalTime):
        self.foundTime = foundTime
        self.totalTime = totalTime

    def setParameters(self, nIter, pu, rho, sigma1, sigma2, sigma3, tau, c, nc, theta, ns):
        self.nIter = nIter
        self.pu = pu
        self.rho = rho
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.sigma3 = sigma3
        self.tau = tau
        self.c = c
        self.nc = nc
        self.theta = theta
        self.ns = ns

    def getCost(self):
        # return self.cost()
        # return self.fitness()
        return self.distance()

    def appendTimeSlot(self, timeSlot):
        self.listTimeSlot.append(timeSlot)

    def removeTimeSlot(self, timeSlotToRemove):
        self.listTimeSlot.remove(timeSlotToRemove)

    def clone(self, solutionToCopy):
        # Copie des variables
        self.instance = solutionToCopy.instance
        self.foundTime = solutionToCopy.foundTime
        self.totalTime = solutionToCopy.totalTime
        self.numberTimeSlotMax = solutionToCopy.numberTimeSlotMax
        self.routePerTimeSlotMax = solutionToCopy.routePerTimeSlotMax
        self.durationTimeSlotMax = solutionToCopy.durationTimeSlotMax

        # Copie des timeslots
        self.listTimeSlot = []
        for timeSlotToCopy in solutionToCopy.listTimeSlot:
            timeSlot = TimeSlot()
            timeSlot.clone(timeSlotToCopy)
            self.listTimeSlot.append(timeSlot)

    def copy(self):
        solution = Solution(self.instance, self.numberTimeSlotMax, self.routePerTimeSlotMax, self.durationTimeSlotMax)
        solution.setTime(self.foundTime, self.totalTime)
        solution.setParameters(self.nIter, self.pu, self.rho, self.sigma1, self.sigma2, self.sigma3, self.tau,
                               self.c, self.nc, self.theta, self.ns)
        for timeslot in self.listTimeSlot:
            solution.appendTimeSlot(timeslot.copy())
        return solution

    def cost(self):
        self.duration = 0
        self.requestPriorityPenalty = 0
        self.inventoryPriorityPenalty = 0

        for indexTimeSlot in range(len(self.listTimeSlot)):
            timeSlot = self.listTimeSlot[indexTimeSlot]

            # Calcul de Z1
            self.duration += timeSlot.getDuration(self.instance.getDistance)

            for route in timeSlot.listRoute:
                if len(route.trajet) > 1:
                    for indexClient in range(len(route.trajet) - 1):
                        clientArrivee = route.getClientByIndex(indexClient + 1)

                        # Calcul de Z2
                        if indexTimeSlot + 1 > 1:
                            self.requestPriorityPenalty += (math.floor(10 * (clientArrivee.ratio()))
                                                            * indexTimeSlot) / 10

                            # Calcul de Z3
                            if clientArrivee.requete:
                                self.inventoryPriorityPenalty += indexTimeSlot

        # Calcul de Z4
        nbTimeSlot = len(self.listTimeSlot)

        # Calcul du coût total
        cost = Solution.facteurZ1 * self.duration + Solution.facteurZ2 * self.requestPriorityPenalty
        cost += Solution.facteurZ3 * self.inventoryPriorityPenalty + Solution.facteurZ4 * nbTimeSlot
        return cost

    def fitness(self, alpha=8, beta=4, gamma=4):
        self.satisfaction = 0
        self.fillRate = 0
        self.usingCost = 0
        self.duration = 0
        notInRoute = {client.indice: 1 for client in self.instance.listClient}

        for timeslot in self.listTimeSlot:
            self.duration += timeslot.getDuration(self.instance.getDistance)

            for route in timeslot.listRoute:
                self.fillRate += route.vehicle.capacity / max(1, route.getTotalQuantity())
                self.usingCost += route.getVehicleCost(self.instance.getDistance)

                for client in route.trajet:
                    notInRoute[client.indice] = 0

            for client in self.instance.listClient:
                self.satisfaction += client.priorite() * notInRoute[client.indice]

        cost = pow(self.satisfaction, alpha) + pow(self.fillRate, beta) + pow(self.usingCost, gamma)
        return cost

    def distance(self):
        dist = 0
        for timeslot in self.listTimeSlot:
            for route in timeslot.listRoute:
                dist += route.getTotalDistance(self.instance.getDistance)
        return dist

    def display(self):
        print("*** Solution {name} ***".format(name=self.instance.name))
        print("- Coût minimisé = {cost}".format(cost=self.getCost()))
        print("- Coût de la solution = {c} (= {k1}*{z1} + {k2}*{z2} + {k3}*{z3} + {k4}*{z4})".format(
            c=round(self.cost(), 2),
            k1=Solution.facteurZ1,
            z1=round(self.duration, 2),
            k2=Solution.facteurZ2,
            z2=round(self.requestPriorityPenalty, 2),
            k3=Solution.facteurZ3,
            z3=self.inventoryPriorityPenalty,
            k4=Solution.facteurZ4,
            z4=len(self.listTimeSlot)))
        print("- Fitness = {f} (= {satisfaction}^8 + {fillRate}^4 + {usingCost}^4)".format(
            f=round(self.fitness(), 2),
            satisfaction=round(self.satisfaction, 2),
            fillRate=round(self.fillRate, 2),
            usingCost=round(self.usingCost, 2)))

        print("- Distance = {d}".format(d=self.distance()))

        print("Found in {t} / {tt} s".format(t=round(self.foundTime, 2), tt=round(self.totalTime, 2)))
        i = 1
        for timeSlot in self.listTimeSlot:
            timeSlot.display(i)
            i += 1
