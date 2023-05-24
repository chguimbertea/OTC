import pandas as pd
import json
from Localisation import Localisation
from Client import Client
from Collecteur import Collecteur


def creer_collecteur(df, index):
    nom = df['name']
    capacite_depot = 1000  # if 'depot_capacity' in df.index else 1000

    # LOCALISATION
    adress = df['depotAdress']
    loc = Localisation()
    if not loc.from_adress(adress):
        loc.from_DD(df['depotLatitude'], df['depotLongitude'])

    # HORAIRES
    debut = df['earliestStart']
    fin = 24 if df['latestEnd'] == 0 else df['latestEnd']
    horaires = [[debut, fin]]

    # VEHICULE
    capacite_vehicule = df['capacity']
    vitesse = df['speed']
    fct = df['fixedCollectionTime']
    ctc = df['collectionTimePerCrate']

    # COST
    fixedCost = df['fixedCost'] if 'fixedCost' in df.index else 0
    kmCost = df['kmCost'] if 'kmCost' in df.index else 0
    crateCost = df['crateCost'] if 'crateCost' in df.index else 0
    stopCost = df['stopCost'] if 'stopCost' in df.index else 0

    return Collecteur(nom, index, loc, capacite_depot, horaires,
                      capacite_vehicule, vitesse, fct, ctc,
                      fixedCost, kmCost, crateCost, stopCost)


def parse_collecteurs(fileName):
    collecteurs = []
    df = pd.read_json(fileName, orient='records')
    df.fillna(0, inplace=True)
    for index, row in df.iterrows():
        i = index
        i += 1000
        collecteurs.append(creer_collecteur(row, i))
    return collecteurs


def creer_client(df, index):
    nom = df['Name']
    quantite = df['quantity']
    capacite = -1 if df['Nb Casiers'] == 0 else df['Nb Casiers']  # pq?!!
    requete = df['request']
    dernier_passage = df['lastCollect']
    loc = Localisation(df['latitude'], df['longitude'])
    horaires = df['hours'] if 'hours' in df.index else None
    return Client(index, quantite, capacite, requete, loc, horaires, dernier_passage, nom)


def parse_clients(fileName):
    clients = []
    df = pd.read_csv(fileName)
    if 'hours' in df.columns:
        df.hours = df.hours.apply(json.loads)
    for index, row in df.iterrows():
        clients.append(creer_client(row, index))
    return clients

