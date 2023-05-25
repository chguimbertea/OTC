import json
import pandas as pd

from Localisation import Localisation
from alns.Instance import Instance
from alns.TimeSlot import TimeSlot
from alns.Route import Route
from alns.Vehicle import Vehicle
from Client import Client
from alns.Solution import Solution
from parser import parse_clients


def findVehicle(dataVehicle, listVehicle):
    name = dataVehicle['name']
    capacity = int(dataVehicle['capacity'])
    speed = float(dataVehicle['speed'])
    for v in listVehicle:
        if v.name == name and v.capacity == capacity and v.speed == speed:
            return v
    fct = float(dataVehicle['fixedCollectionTime'])
    ctc = float(dataVehicle['collectionTimePerCrate'])
    return Vehicle(capacity, speed, fct, ctc, Client(), name=name)


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
    # vérification que tous les clients sont placés ?
    return clients


def readRoute(dataRoute, listClient, listVehicle):
    vehicle = findVehicle(dataRoute['vehicle'][0], listVehicle)
    route = Route(vehicle)
    route.trajet = readClient(dataRoute['route'], listClient)
    if route.vehicle.depot.indice == -1:
        route.vehicle.depot = route.trajet[0]
    return route


def readTimeSlot(dataTimeSlot, listClient, listVehicle, distFunc):
    timeSlot = TimeSlot()
    for dataRoute in dataTimeSlot['timeSlot']:
        route = readRoute(dataRoute, listClient, listVehicle)
        route.getTotalQuantity()
        timeSlot.appendRoute(route)
    timeSlot.getDuration(distFunc)
    return timeSlot


def read_depot(df, name, index):
    adress = df['depotAdress']
    loc = Localisation()
    if not loc.from_adress(adress):
        loc.from_DD(df['depotLatitude'], df['depotLongitude'])

    earliestStart = df['earliestStart']
    latestEnd = 24 if df['latestEnd'] == 0 else df['latestEnd']
    hours = [[earliestStart, latestEnd]]
    return Client(indice=index, localisation=loc, horaires=hours, nom="depot_" + name)


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


def parse_solution_from_files(clientFilePath, vehicleFilPath, solutionPath):
    listClient = parse_clients(clientFilePath)
    listVehicle = read_vehicles(vehicleFilPath)

    data = json.load(open(solutionPath))
    instance = Instance(listClient, listVehicle, data['name'])

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
        timeSlot = readTimeSlot(dataTimeSlot, instance.listClient, instance.listVehicle, instance.getDistance)
        solution.appendTimeSlot(timeSlot)
    solution.cost()
    return solution
