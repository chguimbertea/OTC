import json
import pandas as pd

from Localisation import Localisation
from alns.Instance import Instance
from alns.TimeSlot import TimeSlot
from alns.Route import Route
from Collecteur import Collecteur
from Client import Client
from alns.Solution import Solution
from parser import parse_clients


def findCollecteur(dataCollecteur, listCollecteur):
    name = dataCollecteur['name']
    capacity = int(dataCollecteur['capacity'])
    speed = float(dataCollecteur['speed'])
    for c in listCollecteur:
        if c.nom == name and c.vehicule_capacite == capacity and c.vehicule_vitesse == speed:
            return c
    fct = float(dataCollecteur['fixedCollectionTime'])
    ctc = float(dataCollecteur['collectionTimePerCrate'])
    return Collecteur(nom=name, vehicule_capacite=capacity, vehicule_vitesse=speed,
                      temps_collecte_fixe=fct, temps_collecte_caisse=ctc)


def readClient(dataClients, listClient):
    clients = [Client() for i in dataClients]
    for dataClient in dataClients:
        i = dataClient['id']
        name = dataClient['name']
        client = listClient[i]
        if client.nom != name:
            raise Exception("Wrong id : {id}".format(id=i))
        order = dataClient['order']
        if order < 0 or len(clients) <= order:
            raise Exception("Wrong order : {order}".format(order=order))
        clients[order] = client
    return clients


def readRoute(dataRoute, listClient, listVehicle):
    collecteur = findCollecteur(dataRoute['collector'][0], listVehicle)
    route = Route(collecteur)
    route.trajet = readClient(dataRoute['route'], listClient)
    if route.collecteur.indice == -1:
        route.collecteur = route.trajet[0]
    return route


def readTimeSlot(dataTimeSlot, listClient, listVehicle, distFunc):
    timeSlot = TimeSlot()
    for dataRoute in dataTimeSlot['timeSlot']:
        route = readRoute(dataRoute, listClient, listVehicle)
        route.getTotalQuantity()
        timeSlot.appendRoute(route)
    timeSlot.getDuration(distFunc)
    return timeSlot


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
    loc = Localisation(dfVehicle['depotLatitude'], dfVehicle['depotLongitude'])
    earliestStart = dfVehicle['earliestStart']
    latestEnd = 24 if dfVehicle['latestEnd'] == 0 else dfVehicle['latestEnd']
    hours = [[earliestStart, latestEnd]]

    return Collecteur(nom=name, indice=1000 + index, vehicule_capacite=capacity, vehicule_vitesse=speed,
                      temps_collecte_fixe=fct, temps_collecte_caisse=ctc, localisation=loc, horaires=hours,
                      cout_fixe=fixedCost, cout_km=kmCost, cout_caisse=crateCost, cout_stop=stopCost)


def read_vehicles(fileName):
    dfVehicles = pd.read_json(fileName, orient='records')
    dfVehicles.fillna(0, inplace=True)
    for index, row in dfVehicles.iterrows():
        return read_vehicle(row, index)


def parse_solution_from_files(clientFilePath, vehicleFilPath, solutionPath):
    listClient = parse_clients(clientFilePath)
    collecteur = read_vehicles(vehicleFilPath)

    data = json.load(open(solutionPath))
    instance = Instance(listClient, collecteur, data['name'])

    nIter = data['nIter']
    ntm = data['number max of timeslot']
    rpt = data['number max of route per timeslot']
    dtm = data['duration max per timeslot']
    pu = data['PU']
    rho = data['rho']
    sigma1 = data['sigma1']
    sigma2 = data['sigma2']
    sigma3 = data['sigma3']
    tau = data['tau']
    c = data['C']
    nc = data['Nc']
    theta = data['theta']
    ns = data['Ns']
    foundTime = data['found time']
    totalTime = data['total time']
    solution = Solution(instance, ntm, rpt, dtm)
    solution.setParameters(nIter, pu, rho, sigma1, sigma2, sigma3, tau, c, nc, theta, ns)
    solution.setTime(foundTime, totalTime)

    for dataTimeSlot in data['routing']:
        timeSlot = readTimeSlot(dataTimeSlot, instance.listClient, instance.collecteur, instance.getDistance)
        solution.appendTimeSlot(timeSlot)
    solution.cost()
    return solution
