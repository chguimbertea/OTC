"""
Source from project ALNS 2022, ALEXI OMAR DJAMA
"""


class Customer:
    def __init__(self, indice=-1, quantity=0, capacity=-1, request=0, location=(0, 0), businessHours=None,
                 lastCollect=0, name="point"):
        self.indice = indice
        self.name = name
        self.location = location
        self.quantity = quantity
        self.capacity = capacity
        self.request = request
        self.lastCollect = lastCollect  # Timestamp ?
        if businessHours is None:
            self.businessHours = [[0, 24]]
        else:
            self.businessHours = sorted(businessHours)
        self.visited = False

    def getIndice(self):
        return self.indice

    def getQuantity(self):
        return self.quantity

    def getCapacity(self):
        return self.capacity

    def isRequested(self):
        return self.request > 0

    def getRatio(self):
        return self.quantity / self.capacity

    def getPriority(self):
        return (1 + self.request) * self.getRatio()

    def isVisited(self):
        return self.visited

    def setRequest(self, requested):
        self.request = requested

    def setVisited(self):
        self.visited = True

    def setNotVisited(self):
        self.visited = False

    def display(self):
        print("- Client = {c} : {name}".format(c=self.indice, name=self.name))
        print("\tCapacity = {c}".format(c=self.capacity))
        print("\tQuantity = {q}".format(q=self.quantity))
        print("\tRequested = {r}".format(r=self.request))
        print("\tOpen : {hours}".format(hours=self.businessHours))
        print("\tVisited = {v}".format(v=self.visited))
        print("\tPriority = {p}".format(p=self.getPriority()))
