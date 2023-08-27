"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""


class Route:
    INDICE = 1

    def __init__(self, collecteur, indice=None):
        self.collecteur = collecteur
        self.trajet = [collecteur, collecteur]
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
        for client in self.trajet[1:-1]:
            self.totalQuantity += client.quantite
        return self.totalQuantity

    def getDuration(self, distFunction, toObjectif=False):
        self.duration = 0

        if len(self.trajet) <= 2:
            return self.duration

        alpha = 0
        clientDepart = self.trajet[0]
        for i in range(1, len(self.trajet)):
            clientArrivee = self.trajet[i]

            # time in minutes
            time = distFunction(clientDepart.indice, clientArrivee.indice) / self.collecteur.vehicule_vitesse * 60
            self.duration += time
            self.duration += self.collecteur.temps_collecte_fixe
            if clientArrivee.indice < 999:
                if toObjectif:
                    alpha = (i-1)/2
                self.duration += (self.collecteur.temps_collecte_caisse + alpha) * clientArrivee.quantite

            clientDepart = clientArrivee

        return self.duration

    def getTotalDistance(self, distFunction):
        dist = 0
        for i in range(0, len(self.trajet) - 1):
            dist += distFunction(self.trajet[i].indice, self.trajet[i + 1].indice)
        return dist

    def getVehicleCost(self, distFunction):
        cost = self.collecteur.cout_fixe \
               + (1 + self.collecteur.cout_km) * self.getTotalDistance(distFunction) \
               + self.collecteur.cout_caisse * self.getTotalQuantity() \
               + self.collecteur.cout_stop * (len(self.trajet) - 2)
        return cost

    def collectionTimeByClient(self, client):
        if client.indice > 999:
            return self.collecteur.temps_collecte_fixe
        return self.collecteur.temps_collecte_fixe + self.collecteur.temps_collecte_caisse * client.quantite

    def canPass(self, distFunction):
        client = self.trajet[0]
        passage = 60 * client.horaires[0][0]
        for nextClient in self.trajet[1:]:
            dist = distFunction(client.indice, nextClient.indice)
            travelTime = dist / self.collecteur.vehicule_vitesse * 60  # min
            deltaTime = passage + self.collectionTimeByClient(client) + travelTime
            canPass = False
            for start, end in nextClient.horaires:
                start = 60 * start
                end = 60 * end
                if deltaTime <= end:
                    passage = max(start, deltaTime)
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
        self.collecteur = routeToCopy.collecteur
        self.trajet = [self.collecteur, self.collecteur]

        # Copie des clients
        for clientToCopy in routeToCopy.trajet[1:-1]:
            self.appendClient(clientToCopy)

    def copy(self):
        route = Route(self.collecteur, self.indice)
        for client in self.trajet[1:-1]:
            route.appendClient(client)
        return route

    def display(self, positionInListTimeSlot="", showTimeTable=False):
        print("\tRoute {i} :".format(i=positionInListTimeSlot))
        print("\t\t- Total Quantity = {q}/{c}".format(q=self.totalQuantity, c=self.collecteur.vehicule_capacite))
        print("\t\t- Duration = {d}".format(d=round(self.duration, 2)))
        route = "{i}".format(i=self.trajet[0].indice)
        for client in self.trajet[1:]:
            route += " -> {i}".format(i=client.indice)
        print("\t\t- Trajet : {route}".format(route=route))
        if showTimeTable:
            for client in self.trajet:
                print("\t\tPassage in {h}".format(h=client.horaires))
