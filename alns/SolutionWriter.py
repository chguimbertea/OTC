import json
import os.path
from alns.Solution import Solution


def writeVehicle(vehicle):
    dictVehicle = {
        "name": vehicle.name,
        "capacity": str(vehicle.capacity),
        "speed": str(vehicle.speed),
        "fixedCollectionTime": str(vehicle.fixedCollectionTime),
        "collectionTimePerCrate": str(vehicle.collectionTimePerCrate),
        "fixedCost": str(vehicle.fixedCost),
        "kmCost": str(vehicle.kmCost),
        "crateCost": str(vehicle.crateCost),
        "stopCost": str(vehicle.stopCost)
    }
    return dictVehicle


def writeClient(client, order):
    dictClient = {
        "id": client.indice,
        "order": order,
        "name": client.nom,
        "latitude": client.localisation.to_tuple()[0],
        "longitude": client.localisation.to_tuple()[1]
    }
    return dictClient


def writeRoute(route, idRoute):
    dictRoute = {
        "id": idRoute,
        "duration": route.duration,
        "vehicle": [writeVehicle(route.vehicle)],
        "route": []
    }
    for order in range(len(route.trajet)):
        client = route.trajet[order]
        dictRoute["route"].append(writeClient(client, order))
    return dictRoute


def writeTimeSlot(timeSlot, idTimeSlot):
    dictTimeSlot = {
        "id": idTimeSlot,
        "duration": timeSlot.duration,
        "timeSlot": []
    }
    for idRoute in range(len(timeSlot.listRoute)):
        route = timeSlot.listRoute[idRoute]
        dictTimeSlot["timeSlot"].append(writeRoute(route, idRoute))
    return dictTimeSlot


def toJson(solution, solutionPath="./result/", fileName=None):
    dictResult = {
        "name": solution.instance.name,
        "nIter": solution.nIter,
        "number max of timeslot": solution.numberTimeSlotMax,
        "number max of route per timeslot": solution.routePerTimeSlotMax,
        "duration max per timeslot": solution.durationTimeSlotMax,
        "PU": solution.pu,
        "rho": solution.rho,
        "sigma1": solution.sigma1,
        "sigma2": solution.sigma2,
        "sigma3": solution.sigma3,
        "tau": solution.tau,
        "C": solution.c,
        "Nc": solution.nc,
        "theta": solution.theta,
        "Ns": solution.ns,
        "K1": Solution.facteurZ1,
        "K2": Solution.facteurZ2,
        "K3": Solution.facteurZ3,
        "K4": Solution.facteurZ4,
        "cost": solution.cost(),
        "fitness": solution.fitness(),
        "found time": solution.foundTime,
        "total time": solution.totalTime,
        "routing": []
    }
    for idTimeSlot in range(len(solution.listTimeSlot)):
        timeSlot = solution.listTimeSlot[idTimeSlot]
        dictResult["routing"].append(writeTimeSlot(timeSlot, idTimeSlot))

    if fileName is None:
        fileName = solution.instance.name
    solutionName = solutionPath + fileName + ".json"
    with open(solutionName, "w") as outfile:
        json.dump(dictResult, outfile, indent=4)
    print("Solution is saved in " + solutionName)
    del dictResult


def toCsv(solution, solutionPath="./result/", fileName=None, reset=False):
    if fileName is None:
        fileName = solution.instance.name
    solutionName = solutionPath + fileName + ".csv"
    if not os.path.isfile(solutionName) or reset:
        with open(solutionName, "w") as outfile:
            outfile.write("Cost; Time; Duration; Request priority penalty; Inventory priority penalty; "
                          "Number of time slots used; Number of iterations; Pu; Rho; Sigma 1; Sigma 2; Sigma 3; Tau; "
                          "C; Nc; Theta; Ns\n")
    with open(solutionName, "a") as outfile:
        line = "{cost}; {time}; {duration}; {request}; {inventory}; " \
               "{timeSlots}; {nIter}; {pu}; {rho}; {sigma1}; {sigma2}; {sigma3}; {tau}; " \
               "{c}; {nc}; {theta}; {ns}; {ntm}; {rpt}; {dtm}\n".format(cost=solution.cost(),
                                                                        time=solution.foundTime,
                                                                        duration=solution.duration,
                                                                        request=solution.requestPriorityPenalty,
                                                                        inventory=solution.inventoryPriorityPenalty,
                                                                        timeSlots=len(solution.listTimeSlot),
                                                                        nIter=solution.nIter,
                                                                        pu=solution.pu,
                                                                        rho=solution.rho,
                                                                        sigma1=solution.sigma1,
                                                                        sigma2=solution.sigma2,
                                                                        sigma3=solution.sigma3,
                                                                        tau=solution.tau,
                                                                        c=solution.c,
                                                                        nc=solution.nc,
                                                                        theta=solution.theta,
                                                                        ns=solution.ns,
                                                                        ntm=solution.numberTimeSlotMax,
                                                                        rpt=solution.routePerTimeSlotMax,
                                                                        dtm=solution.durationTimeSlotMax
                                                                        )
        outfile.write(line)
    print("Solution is writen in " + solutionName)
