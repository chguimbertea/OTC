import pandas as pd
import json
from geopy.geocoders import Nominatim
from alns.Instance import Instance
from Client import Client
from alns.Vehicle import Vehicle


def read_depot(df, name, index):
    adress = df['depotAdress'] if 'depotAdress' in df.index else None
    if {'depotLatitude', 'depotLongitude'}.issubset(df.index):
        location = (df['depotLatitude'], df['depotLongitude'])
    else:
        geocoder = Nominatim(user_agent="myGeocoder")
        location = geocoder.geocode(adress)
        if location is None:
            raise Exception("Wrong adress : " + adress)
        location = (location.latitude, location.longitude)
    earliestStart = df['earliestStart']
    latestEnd = 24 if df['latestEnd'] == 0 else df['latestEnd']
    hours = [[earliestStart, latestEnd]]
    return Client(indice=index, localisation=location, horaires=hours, nom="depot_" + name)


def read_vehicle(dfVehicle, index):
    name = dfVehicle['name']
    capacity = dfVehicle['capacity']
    speed = dfVehicle['speed']
    fct = dfVehicle['fixedCollectionTime']
    ctc = dfVehicle['collectionTimePerCrate']

    # COST

    fixedCost = dfVehicle['fixedCost']
    kmCost = dfVehicle['kmCost']
    crateCost = dfVehicle['crateCost']
    stopCost = dfVehicle['stopCost']

    # DEPOT
    depot = read_depot(dfVehicle, name, index)

    return Vehicle(capacity, speed, fct, ctc, depot, fixedCost, kmCost, crateCost, stopCost, name)


def read_vehicles(fileName):
    listVehicle = []
    dfVehicles = pd.read_json(fileName, orient='records')
    # if 'fixedCost' not in dfVehicle.index:
    # dfVehicle['fixedCost'][0] = 0
    dfVehicles.fillna(0, inplace=True)
    for index, row in dfVehicles.iterrows():
        i = index
        i += 1000
        listVehicle.append(read_vehicle(row, i))
    return listVehicle


def read_client(dfClient, index):
    name = dfClient['Name']
    quantity = dfClient['quantity']
    capacity = dfClient['Nb Casiers']
    request = dfClient['request']
    lastCollect = dfClient['lastCollect']
    location = (dfClient['latitude'], dfClient['longitude'])
    businessHours = dfClient['hours'] if 'hours' in dfClient.index else None
    if capacity == 0:
        return Client(indice=index, nom=name, quantite=quantity, requete=request, localisation=location,
                      dernier_passage=lastCollect, horaires=businessHours)
    return Client(indice=index, nom=name, quantite=quantity, capacite=capacity, requete=request, localisation=location,
                  dernier_passage=lastCollect, horaires=businessHours)


def read_clients(fileName):
    listClient = []
    dfClient = pd.read_csv(fileName)
    if 'hours' in dfClient.columns:
        dfClient.hours = dfClient.hours.apply(json.loads)
    for index, row in dfClient.iterrows():
        client = read_client(row, index)
        listClient.append(client)
    return listClient


def read_context(fileName):
    dfContext = pd.read_json(fileName, orient='index').transpose()
    name = dfContext['name'][0]
    ntm = dfContext['numberTimeSlotMax'][0]
    rpt = dfContext['routePerTimeSlotMax'][0]
    dtm = dfContext['durationTimeSlotMax'][0]
    return name, ntm, rpt, dtm


def parseWithContext(filePath):
    listVehicle = read_vehicles(filePath + "vehicle.json")
    listClient = read_clients(filePath + "points.csv")
    name, ntm, rpt, dtm = read_context(filePath + "context.json")
    return Instance(listClient, listVehicle, name), ntm, rpt, dtm


def parse(folderPath):
    begin = folderPath[:-1].rfind('/')
    name = folderPath[begin + 1:-1]
    listVehicle = read_vehicles(folderPath + "vehicle.json")
    listClient = read_clients(folderPath + "points.csv")
    return Instance(listClient, listVehicle, name)
