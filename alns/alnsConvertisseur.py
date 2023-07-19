from Client import Client
from alns.ALNS import ALNS
from alns.Instance import Instance
from alns.Vehicle import Vehicle


def collecteurToVehicle(collecteur):
    depot = Client(indice=collecteur.indice, localisation=collecteur.localisation,
                   horaires=collecteur.horaires, nom="depot_" + collecteur.nom)
    return Vehicle(collecteur.vehicule_capacite, collecteur.vehicule_vitesse,
                   collecteur.temps_collecte_fixe, collecteur.temps_collecte_caisse, depot,
                   collecteur.cout_fixe, collecteur.cout_km, collecteur.cout_caisse, collecteur.cout_stop,
                   collecteur.vehicule_type, collecteur.nom)


def solve(clients, collecteur, showLog=False):
    vehicule = collecteurToVehicle(collecteur)
    instance = Instance(clients, vehicule)
    methode = ALNS(instance)
    solution = methode.solve(withSwap=False, showLog=showLog)

    ordre = []
    for timeSlot in solution.listTimeSlot:
        for route in timeSlot.listRoute:
            if ordre and route.trajet[0].indice == ordre[-1].indice:
                continue
            for client in route.trajet:
                ordre.append(client)

    return ordre
