"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from methodes import distance


class Instance:
    def __init__(self, listClient, vehicle, name="present"):
        self.listClient = listClient.copy()
        self.vehicle = vehicle
        self.name = name

        # DISTANCE BETWEEN EVERY POINT
        tmpListPoint = listClient.copy()
        tmpListPoint.append(vehicle.depot)
        self.distTravel = {(i.indice, j.indice): distance(i.localisation, j.localisation, vehicle.type)
                           for i in tmpListPoint for j in tmpListPoint if i.indice < j.indice}  # km

    def getDistance(self, firstClientId, secondClientId):  # km
        if firstClientId == secondClientId:
            return 0
        return self.distTravel[(min(firstClientId, secondClientId), max(firstClientId, secondClientId))]

    def display(self, showDistTravel=False):
        # showDistTravel est un booléen correspondant à l'affichage de la distance entre chaque client
        print("--- Instance {name} ---".format(name=self.name))

        print("* List of clients :")
        for client in self.listClient:
            client.display()

        print("* Vehicles :")
        self.vehicle.display()

        if showDistTravel:
            print("* Distance travel :")
            for key, value in self.distTravel.items():
                print("\t-{cle} : {valeur}".format(cle=key, valeur=value))
