"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""
from alns.Route import Route


class TimeSlot:
    INDICE = 1

    def __init__(self, indice=None):
        self.listRoute = []
        self.duration = 0
        if indice is None:
            self.indice = TimeSlot.INDICE
            TimeSlot.INDICE += 1
        else:
            self.indice = indice

    def appendRoute(self, route):
        self.listRoute.append(route)

    def removeRoute(self, routeToRemove):
        self.listRoute.remove(routeToRemove)

    def getDuration(self, distFunction):
        s = 0
        for route in self.listRoute:
            s += route.getDuration(distFunction)
        self.duration = s
        return self.duration

    def clone(self, timeSlotToCopy):
        # Copie des variables
        self.indice = timeSlotToCopy.indice
        self.duration = timeSlotToCopy.duration

        # Copie des routes
        self.listRoute = []
        for routeToCopy in timeSlotToCopy.listRoute:
            route = Route(routeToCopy.vehicle)
            route.clone(routeToCopy)
            self.appendRoute(route)

    def copy(self):
        timeslot = TimeSlot(self.indice)
        for route in self.listRoute:
            timeslot.appendRoute(route.copy())
        return timeslot

    def display(self, positionInList=""):
        i = 1
        print("*** Time slot {i} ***".format(i=positionInList))
        print("\t- Duration = {d}".format(d=round(self.duration, 2)))
        print("\t- Nombre de routes = {r}".format(r=len(self.listRoute)))
        for route in self.listRoute:
            route.display(i)
            if i < len(self.listRoute):
                print()
            i += 1
        print()
