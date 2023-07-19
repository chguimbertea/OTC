import pandas as pd
import json
from Localisation import Localisation
from Client import Client
from Collecteur import Collecteur


def parse_contexte(fileName):
    df = pd.read_json(fileName, orient='index')
    name = df.at['name', 0]
    ntm = df.at['numberTimeSlotMax', 0]
    rtm = df.at['routePerTimeSlotMax', 0]
    dtm = df.at['durationTimeSlotMax', 0]
    return name, ntm, rtm, dtm


def creer_collecteur(df, index):
    nom = df['nom']
    capacite_depot = df['depotCapacite'] if 'depotCapacite' in df.index else 1000

    # LOCALISATION
    adress = df['depotAdresse']
    loc = Localisation()
    if not loc.from_adress(adress):
        loc.from_DD(df['depotLatitude'], df['depotLongitude'])

    # HORAIRES
    horaires = df['horaires']

    # VEHICULE
    capacite_vehicule = df['capacite']
    vitesse = df['vitesse']
    fct = df['tempsCollecteFixe']
    ctc = df['tempsCollecteCaisse']

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
    nom = df['nom']
    quantite = df['quantite']
    capacite = -1 if df['capacite'] == 0 else df['capacite']  # pq?!!
    requete = df['requete']
    dernier_passage = df['derniere collecte'] if 'derniere collecte' in df.index else 0
    loc = Localisation(df['latitude'], df['longitude'])
    horaires = df['horaires'] if 'horaires' in df.index else []
    return Client(index, quantite, capacite, requete, loc, horaires, dernier_passage, nom)


def parse_clients(fileName):
    clients = []
    df = pd.read_csv(fileName)
    for index, row in df.iterrows():
        clients.append(creer_client(row, index))
    return clients

