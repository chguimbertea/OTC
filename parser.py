import pandas as pd
import ast
from Localisation import Localisation
from Client import Client
from Collecteur import Collecteur


def creer_collecteur(df, index):
    nom = df['nom']

    # LOCALISATION
    adress = df['depotAdresse']
    loc = Localisation()
    #if not loc.from_adress(adress):
    #    loc.from_DD(df['depotLatitude'], df['depotLongitude'])
    loc.from_DD(df['depotLatitude'], df['depotLongitude'])

    # HORAIRES
    horaires = None if df['horaires'] == 0 else df['horaires']

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

    return Collecteur(nom, index, loc, horaires,
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


def creer_new_collecteur(df, index):
    nom = df['Name']

    # LOCALISATION
    adress = df['Adresse 1'] + ', ' + str(df['Code postal']) + ', ' + df['Ville']
    loc = Localisation()
    if not loc.from_adress(adress):
        loc.from_DD(df['latitude'], df['longitude'])


    # HORAIRES
    horaires = None if df['horaires'] == 0 else df['horaires']

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

    return Collecteur(nom, index, loc, horaires,
                      capacite_vehicule, vitesse, fct, ctc,
                      fixedCost, kmCost, crateCost, stopCost)


def parse_new_collecteurs(fileName):
    collecteurs = []
    df = pd.read_csv(fileName)
    df.fillna(0, inplace=True)
    for index, row in df.iterrows():
        i = index
        i += 1000
        collecteurs.append(creer_collecteur(row, i))
    return collecteurs

def creer_client(df, index, ajd):
    nom = df['Name']
    quantite = df['quantite']
    capacite = df['Nb Casiers']
    if capacite == 0:
        # par sécurité, on ne veut pas de division par 0
        capacite = -1
    requete = df['demande']
    loc = Localisation(df['latitude'], df['longitude'])
    horaires = ast.literal_eval(df['heures']) if 'heures' in df.index else None

    qualite_tri = df['Qualité de collecte'] if 'Qualité de collecte' in df.index else 'NEUTRE'
    if qualite_tri == 'TOPISSIME':
        qualite_tri = 1
    elif qualite_tri == 'NEUTRE':
        qualite_tri = 0
    else:
        qualite_tri = -1

    if 'date' in df.index and df['date']:
        jours_depuis_collecte = (ajd - pd.Timestamp(df['date'])).days
    else:
        jours_depuis_collecte = 0

    collecteurs_dispo = df['Collecteurs disponibles']

    return Client(indice=index, nom=nom, quantite=quantite, capacite=capacite, requete=requete, localisation=loc,
                  horaires=horaires, jours_depuis_collecte=jours_depuis_collecte, qualite_tri=qualite_tri,
                  collecteurs_disponibles=collecteurs_dispo)


def parse_clients(fileName, jour=pd.Timestamp.today()):
    clients = []
    df = pd.read_csv(fileName)
    for index, row in df.iterrows():
        clients.append(creer_client(row, index, jour))
    return clients

