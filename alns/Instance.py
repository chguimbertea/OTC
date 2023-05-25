"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from methodes import distance


class Instance:
    def __init__(self, listClient, listVehicle, name="present"):
        self.listClient = listClient.copy()
        self.listVehicle = listVehicle
        self.name = name

        # DISTANCE BETWEEN EVERY POINT
        tmpListPoint = listClient.copy()
        for vehicle in self.listVehicle:
            if vehicle.depot.indice == -1:
                continue
            tmpListPoint.append(vehicle.depot)
        self.distTravel = {(i.indice, j.indice): distance(i.localisation, j.localisation)
                           for i in tmpListPoint for j in tmpListPoint if i.indice < j.indice}  # km

    def getDistance(self, firstClientId, secondClientId):  # km
        if firstClientId == secondClientId:
            return 0
        return self.distTravel[(min(firstClientId, secondClientId), max(firstClientId, secondClientId))]

    def copy(self):
        return Instance(self.listClient.copy(), self.listVehicle.copy(), self.name)

    def display(self, showDistTravel=False):
        # showClients est un boolean correspondant à l'affichage la liste des clients
        # showDistTravel est un boolean correspondant à l'affichage de la distance entre chaque client
        print("--- Instance {name} ---".format(name=self.name))

        print("* List of clients :")
        for client in self.listClient:
            client.display()

        print("* List of vehicles :")
        for vehicle in self.listVehicle:
            vehicle.display()

        if showDistTravel:
            print("* Distance travel :")
            for cle, valeur in self.distTravel.items():
                print("\t-{cle} : {valeur}".format(cle=cle, valeur=valeur))
