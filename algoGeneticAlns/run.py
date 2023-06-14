from algoGeneticAlns import algo
from parser import parse_collecteurs, parse_clients
from Client import Client
from alns.ALNS import ALNS
from alns.Instance import Instance
from alns.Vehicle import Vehicle

collecteur = parse_collecteurs("data/Medium6/vehicle.json")[0]
clients = parse_clients("data/Medium6/points.csv")

depot = Client(indice=collecteur.indice, localisation=collecteur.localisation,
               horaires=collecteur.horaires, nom="depot_" + collecteur.nom)
vehicle = Vehicle(collecteur.vehicule_capacite, collecteur.vehicule_vitesse,
                  collecteur.temps_collecte_fixe, collecteur.temps_collecte_caisse,
                  depot,
                  collecteur.cout_fixe, collecteur.cout_km, collecteur.cout_caisse, collecteur.cout_stop,
                  collecteur.vehicule_type, collecteur.nom)

instance = Instance(clients, vehicle)
methode = ALNS(instance)

algo.setup(methode, pop_size=100)
n = 1000
for i in range(n):
    algo.run()
