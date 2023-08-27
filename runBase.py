import sys

import pandas as pd
from Localisation import Localisation
from Client import Client
from Collecteur import Collecteur
from alns.Instance import Instance
from alns.ALNS import ALNS


def parse_contexte(fileName):
    df = pd.read_json(fileName, orient='index')
    name = df.at['name', 0]
    ntm = df.at['numberTimeSlotMax', 0]
    rtm = df.at['routePerTimeSlotMax', 0]
    dtm = df.at['durationTimeSlotMax', 0]
    return name, ntm, rtm, dtm


def creer_collecteur(df, index):
    nom = df['nom']

    # LOCALISATION
    adress = df['depotAdresse']
    loc = Localisation()
    if not loc.from_adress(adress):
        loc.from_DD(df['depotLatitude'], df['depotLongitude'])

    # VEHICULE
    capacite_vehicule = df['capacite']
    vitesse = df['vitesse']
    fct = df['tempsCollecteFixe']
    ctc = df['tempsCollecteCaisse']

    return Collecteur(nom=nom, indice=index, localisation=loc, vehicule_capacite=capacite_vehicule,
                      vehicule_vitesse=vitesse, temps_collecte_fixe=fct, temps_collecte_caisse=ctc)


def parse_collecteurs(fileName):
    collecteurs = []
    df = pd.read_json(fileName, orient='records')
    df.fillna(0, inplace=True)
    for index, row in df.iterrows():
        i = index
        i += 1000
        collecteurs.append(creer_collecteur(row, i))
    return collecteurs


def parse_clients(fileName):
    clients = []
    df = pd.read_csv(fileName)
    for index, row in df.iterrows():
        nom = row['nom']
        quantite = row['quantite']
        capacite = row['capacite']
        requete = row['requete']
        loc = Localisation(row['latitude'], row['longitude'])
        client = Client(indice=index, nom=nom, quantite=quantite, capacite=capacite, requete=requete, localisation=loc)
        clients.append(client)
    return clients


"""
Si obj = "cost", alors les résultats attendus :
    Objectif de dataBase = 226.0928
    Chemins :
        1000 -> 1 -> 0 -> 11 -> 8 -> 7 -> 6 -> 5 -> 10 -> 2 -> 1000
        1000 -> 3 -> 4 -> 9 -> 1000


Si obj = "distance", alors les résultats attendus :
    Objectif = 52.791
    Chemins :
        1000 -> 10 -> 9 -> 5 -> 6 -> 7 -> 8 -> 11 -> 0 -> 1000
        1000 -> 2 -> 1 -> 4 -> 3 -> 1000
        
Si obj = "duration", alors les résultats attendus :
    Objectif = 294.431
    Chemins :
        1000 -> 3 -> 4 -> 2 -> 1000
        1000 -> 0 -> 11 -> 7 -> 8 -> 1 -> 1000
        1000 -> 9 -> 5 -> 6 -> 10 -> 1000
"""

if __name__ == "__main__":
    # LECTURE DES DONNÉES
    filePath = "dataBase"
    if len(sys.argv) > 2:
        filePath = sys.argv[1]
    collecteur = parse_collecteurs(filePath+"/vehicule.json")[0]
    clients = parse_clients(filePath+"/points.csv")
    nom, ntm, rtm, dtm = parse_contexte(filePath+"/contexte.json")

    # objectif : {"cost", "distance", "duration"}
    objectif = "cost"
    if len(sys.argv) > 2:
        obj = sys.argv[2]
        if obj in ["cost", "distance", "duration"]:
            objectif = obj

    instance = Instance(clients, collecteur, nom, obj=objectif)
    methode = ALNS(instance, ntm, rtm, dtm)
    solution = methode.solve(withSwap=False)
    solution.display()
