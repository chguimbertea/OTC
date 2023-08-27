from alns.ALNS import ALNS
from alns.Instance import Instance


def solve(clients, collecteur, showLog=False):
    instance = Instance(clients, collecteur, obj="distance")
    methode = ALNS(instance)
    solution = methode.solve(withSwap=False, showLog=showLog)

    ordre = []
    for timeSlot in solution.listTimeSlot:
        for route in timeSlot.listRoute:
            if ordre and route.trajet[0].indice == ordre[-1].indice:
                continue
            for client in route.trajet:
                ordre.append(client)

    return ordre
