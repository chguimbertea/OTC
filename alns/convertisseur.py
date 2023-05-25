from Client import Client
from alns.ALNS import ALNS
from alns.Instance import Instance
from alns.Vehicle import Vehicle


def solve(list_client, collecteur):
    new_list_client = list_client

    new_list_vehicle = []
    id_depot = 1000
    depot = Client(indice=id_depot, localisation=collecteur.localisation,
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

    dict_client = {c.indice: c for c in list_client}
    dict_client[id_depot] = collecteur
    order = []
    for timeSlot in solution.listTimeSlot:
        for route in timeSlot.listRoute:
            if not order:
                order.append(dict_client[route.trajet[0].indice])
            for client in route.trajet[1:]:
                order.append(dict_client[client.indice])

    return order
