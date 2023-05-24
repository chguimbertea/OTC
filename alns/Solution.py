"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from alns.Route import Route
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
        """cost = 0
        for timeslot in self.listTimeSlot:
            for route in timeslot.listRoute:
                cost += route.getVehicleCost(self.instance.getDistance)
        """
        # cost = self.cost()
        # cost = self.fitness()
        cost = self.distance()
        return cost

    def getListTimeSlot(self):
        return self.listTimeSlot

    def appendTimeSlot(self, timeSlot):
        self.listTimeSlot.append(timeSlot)

    def removeTimeSlot(self, timeSlotToRemove):
        i = 0
        for timeSlot in self.listTimeSlot:
            if timeSlot.getIndice() == timeSlotToRemove.getIndice():
                break
            i += 1
        self.listTimeSlot.pop(i)

    def setSingleRouteFromClient(self, listClient, vehicle):
        self.listTimeSlot = []
        for client in listClient:
            timeslot = TimeSlot()
            route = Route(vehicle)
            route.appendClient(client)
            timeslot.appendRoute(route)
            self.listTimeSlot.append(timeslot)

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

            for route in timeSlot.getListRoute():
                if len(route.getTrajet()) > 1:
                    for indexClient in range(len(route.getTrajet()) - 1):
                        clientArrivee = route.getClientByIndex(indexClient + 1)

                        # Calcul de Z2
                        if indexTimeSlot + 1 > 1:
                            self.requestPriorityPenalty += (math.floor(10 * (clientArrivee.getRatio()))
                                                            * indexTimeSlot) / 10

                            # Calcul de Z3
                            if clientArrivee.isRequested():
                                self.inventoryPriorityPenalty += indexTimeSlot

        # Calcul de Z4
        nbTimeSlot = len(self.listTimeSlot)

        # Calcul du coût total
        cost = Solution.facteurZ1 * self.duration + Solution.facteurZ2 * self.requestPriorityPenalty
        cost += Solution.facteurZ3 * self.inventoryPriorityPenalty + Solution.facteurZ4 * nbTimeSlot
        return cost

    def fitness(self, alpha=1, beta=1, gamma=1):
        self.satisfaction = 0
        self.fillRate = 0
        self.usingCost = 0
        self.duration = 0
        notInRoute = {client.getIndice(): 1 for client in self.instance.listClient}

        for timeslot in self.listTimeSlot:
            self.duration += timeslot.getDuration(self.instance.getDistance)

            for route in timeslot.getListRoute():
                self.fillRate += route.vehicle.getCapacity() / max(1, route.getTotalQuantity())
                self.usingCost += route.getVehicleCost(self.instance.getDistance)

                for client in route.getTrajet():
                    notInRoute[client.getIndice()] = 0

            for client in self.instance.listClient:
                self.satisfaction += client.getPriority() * notInRoute[client.getIndice()]

        # cost = alpha * self.satisfaction + beta * self.fillRate + gamma * self.usingCost
        cost = pow(self.satisfaction, 8) + pow(self.fillRate, 4) + pow(self.usingCost, 4)
        return cost

    def distance(self):
        dist = 0
        for timeslot in self.listTimeSlot:
            for route in timeslot.listRoute:
                dist += route.getTotalDistance(self.instance.getDistance)
        return dist

    def display(self, name=None):
        name = self.instance.getName() if name is None else name
        print("*** Solution {name} ***".format(name=name))
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
        print("- Fitness = {f} (= alpha*{satisfaction}^8 + beta*{fillRate}^4 + gamma*{usingCost}^4)".format(
            f=round(self.fitness(), 2),
            satisfaction=round(self.satisfaction, 2),
            fillRate=round(self.fillRate, 2),
            usingCost=round(self.usingCost, 2)))

        dist = 0
        for timeslot in self.listTimeSlot:
            for route in timeslot.listRoute:
                dist += route.getTotalDistance(self.instance.getDistance)
        print("- Distance = {d}".format(d=dist))

        print("Found in {t} / {tt} s".format(t=round(self.foundTime, 2), tt=round(self.totalTime, 2)))
        i = 1
        for timeSlot in self.listTimeSlot:
            timeSlot.display(i)
            i += 1
