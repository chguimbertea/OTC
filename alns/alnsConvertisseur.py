from Client import Client
from alns.ALNS import ALNS
from alns.Instance import Instance
from alns.Vehicle import Vehicle


def solve(list_client, collecteur):
    new_list_client = list_client

    new_list_vehicle = []
    depot = Client(indice=collecteur.indice, localisation=collecteur.localisation,
                   horaires=collecteur.horaires, nom="depot_" + collecteur.nom)
    v = Vehicle(collecteur.vehicule_capacite, collecteur.vehicule_vitesse,
                collecteur.temps_collecte_fixe, collecteur.temps_collecte_caisse,
                depot,
                collecteur.cout_fixe, collecteur.cout_km, collecteur.cout_caisse, collecteur.cout_stop,
                collecteur.nom)
    new_list_vehicle.append(v)

    instance = Instance(new_list_client, new_list_vehicle)
    methode = ALNS(instance)
    solution = methode.solve()

    ordre = []
    for timeSlot in solution.listTimeSlot:
        for route in timeSlot.listRoute:
            if ordre and route.trajet[0].indice == ordre[-1].indice:
                continue
            for client in route.trajet:
                ordre.append(client)

    return ordre
