"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""


class Route:
    INDICE = 1

    def __init__(self, vehicle, indice=None):
        self.vehicle = vehicle
        if self.vehicle.depot.indice == -1:
            raise Exception("Vehicle without depot can't start a route")
        self.trajet = [vehicle.depot, vehicle.depot]
        self.totalQuantity = 0
        self.duration = 0
        if indice is None:
            self.indice = Route.INDICE
            Route.INDICE += 1
        else:
            self.indice = indice

    def isEmpty(self):
        return len(self.trajet) <= 2

    def getClientByIndex(self, index):
        size = len(self.trajet)
        if size <= index or index < -size:
            raise Exception("Invalid index : {i}".format(i=index))
        return self.trajet[index]

    def appendClient(self, client):
        if client.indice > 999:
            return
        self.insertClient(-1, client)

    def insertClient(self, index, client):
        size = len(self.trajet)
        if index > size - 1:
            index = -1
        elif index == 0 or index <= -size:
            index = 1
        self.trajet.insert(index, client)
        self.totalQuantity += client.quantite

    def removeClient(self, clientToRemove):
        i = 0
        for client in self.trajet:
            if clientToRemove.indice == client.indice:
                break
            i = i + 1
        return self.removeClientByPosition(i)

    def removeClientByPosition(self, index):
        size = len(self.trajet)
        if size <= index or index < -size:
            raise Exception("Invalid index : {i}".format(i=index))
        if index == 0 or index == -size or index == size-1 or index == -1:
            raise Exception("Can't remove depot in route")
        client = self.trajet.pop(index)
        self.totalQuantity -= client.quantite
        return client

    def getTotalQuantity(self):
        self.totalQuantity = 0
        for client in self.trajet:
            self.totalQuantity += client.quantite
        return self.totalQuantity

    def getDuration(self, distFunction):
        self.duration = 0

        if len(self.trajet) <= 2:
            return self.duration

        clientDepart = self.trajet[0]
        for i in range(1, len(self.trajet)):
            clientArrivee = self.trajet[i]

            # time in minutes
            time = distFunction(clientDepart.indice,
                                clientArrivee.indice) / self.vehicle.speed * 60
            self.duration += time
            self.duration += self.vehicle.fixedCollectionTime
            self.duration += self.vehicle.collectionTimePerCrate * clientArrivee.quantite

            clientDepart = clientArrivee

        return self.duration

    def getTotalDistance(self, distFunction):
        dist = 0
        for i in range(0, len(self.trajet) - 1):
            dist += distFunction(self.trajet[i].indice, self.trajet[i + 1].indice)
        return dist

    def getVehicleCost(self, distFunction):
        cost = self.vehicle.fixedCost \
               + (1 + self.vehicle.kmCost) * self.getTotalDistance(distFunction) \
               + self.vehicle.crateCost * self.getTotalQuantity() \
               + self.vehicle.stopCost * (len(self.trajet) - 2)
        return cost

    def collectionTimeByClient(self, client):
        if client.indice > 999:
            return 0
        return self.vehicle.fixedCollectionTime + self.vehicle.collectionTimePerCrate * client.quantite

    def canPass(self, distFunction):
        client = self.trajet[0]
        passage = 60 * client.horaires[0][0]
        allpassage = [passage / 60]
        for nextClient in self.trajet[1:]:
            dist = distFunction(client.indice, nextClient.indice)
            travelTime = dist / self.vehicle.speed * 60  # min
            deltaTime = passage + self.collectionTimeByClient(client) + travelTime
            canPass = False
            for start, end in nextClient.horaires:
                start = 60 * start
                end = 60 * end
                if deltaTime <= end:
                    passage = max(start, deltaTime)
                    allpassage.append(passage / 60)
                    canPass = True
                    break
            if not canPass:
                return False
            client = nextClient
        return True

    def clone(self, routeToCopy):
        # Copie des variables
        self.indice = routeToCopy.indice
        self.duration = routeToCopy.duration
        self.totalQuantity = 0
        self.vehicle = routeToCopy.vehicle
        self.trajet = [self.vehicle.depot, self.vehicle.depot]

        # Copie des clients
        for clientToCopy in routeToCopy.trajet:
            self.appendClient(clientToCopy)

    def copy(self):
        route = Route(self.vehicle, self.indice)
        for client in self.trajet:
            route.appendClient(client)
        return route

    def display(self, positionInListTimeSlot="", showTimeTable=False):
        print("\tRoute {i} :".format(i=positionInListTimeSlot))
        print("\t\t- Total Quantity = {q}/{c}".format(q=self.totalQuantity, c=self.vehicle.capacity))
        print("\t\t- Duration = {d}".format(d=round(self.duration, 2)))
        route = "{i}".format(i=self.trajet[0].indice)
        for client in self.trajet[1:]:
            route += " -> {i}".format(i=client.indice)
        print("\t\t- Trajet : {route}".format(route=route))
        if showTimeTable:
            for client in self.trajet:
                print("\t\tPassage in {h}".format(h=client.horaires))
