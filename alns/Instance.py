"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
import geopy.distance as gd


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
        self.distTravel = {(i.indice, j.indice): gd.geodesic(i.localisation.to_tuple(), j.localisation.to_tuple()).km
                           for i in tmpListPoint for j in tmpListPoint}

    def getDistance(self, firstClientId, secondClientId):  # km
        return self.distTravel[(firstClientId, secondClientId)]

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
