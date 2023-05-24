
class Vehicle:
    def __init__(self, capacity, speed, fixedCollectionTime, collectionTimePerCrate, depot,
                 fixedCost=0, kmCost=0, crateCost=0, stopCost=0, name="truck"):
        self.name = name
        self.depot = depot
        self.capacity = capacity
        self.speed = speed  # km/h
        self.fixedCollectionTime = fixedCollectionTime
        self.collectionTimePerCrate = collectionTimePerCrate
        self.fixedCost = fixedCost
        self.kmCost = kmCost
        self.crateCost = crateCost
        self.stopCost = stopCost

    def getName(self):
        return self.name

    def getCapacity(self):
        return self.capacity

    def getSpeed(self):  # km/h
        return self.speed

    def getFixedCollectionTime(self):
        return self.fixedCollectionTime

    def getCollectionTimePerCrate(self):
        return self.collectionTimePerCrate

    def getCost(self):
        return self.fixedCost

    def display(self):
        print("- Vehicle : {v}".format(v=self.name))
        print("\tDepot n°{n}".format(n=self.depot.getIndice()))
        print("\tCapacity = {c}".format(c=self.capacity))
        print("\tSpeed = {s}".format(s=self.speed))
        print("\tFixed collection time = {f}".format(f=self.fixedCollectionTime))
        print("\tCollection time per crate = {c}".format(c=self.collectionTimePerCrate))
        print("\tCosts :")
        print("\t\tFixed = {c}".format(c=self.fixedCost))
        print("\t\tPer km = {c}".format(c=self.kmCost))
        print("\t\tPer crate = {c}".format(c=self.crateCost))
        print("\t\tPer stop = {c}".format(c=self.stopCost))
