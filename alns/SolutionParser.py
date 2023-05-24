import json
from alns.TimeSlot import TimeSlot
from alns.Route import Route
from alns.Vehicle import Vehicle
from alns.Customer import Customer
from alns.Solution import Solution
from alns.InstanceParser import parse


def findVehicle(dataVehicle, listVehicle):
    name = dataVehicle['name']
    capacity = int(dataVehicle['capacity'])
    speed = float(dataVehicle['speed'])
    for v in listVehicle:
        if v.getName() == name and v.getCapacity() == capacity and v.getSpeed() == speed:
            return v
    fct = float(dataVehicle['fixedCollectionTime'])
    ctc = float(dataVehicle['collectionTimePerCrate'])
    return Vehicle(capacity, speed, fct, ctc, Customer(), name=name)


def readClient(dataClients, listClient):
    clients = [Customer() for i in dataClients]
    for dataClient in dataClients:
        i = dataClient['id']
        name = dataClient['name']
        client = listClient[i]
        if client.name != name:
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
    if route.vehicle.depot.getIndice() == -1:
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


def parse_solution(instance, solutionPath):
    data = json.load(open(solutionPath))
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


def parse_solution_from_files(filePath, solutionPath):
    instance = parse(filePath)
    # data = json.load(open(solutionPath))
    # instance = parse(data['name'])
    return parse_solution(instance, solutionPath)
