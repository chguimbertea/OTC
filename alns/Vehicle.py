
class Vehicle:
    def __init__(self, capacity, speed, fixedCollectionTime, collectionTimePerCrate, depot,
                 fixedCost=0, kmCost=0, crateCost=0, stopCost=0, typeV="car", name="truck"):
        self.name = name
        self.depot = depot
        self.type = typeV
        self.capacity = capacity
        self.speed = speed  # km/h
        self.fixedCollectionTime = fixedCollectionTime
        self.collectionTimePerCrate = collectionTimePerCrate
        self.fixedCost = fixedCost
        self.kmCost = kmCost
        self.crateCost = crateCost
        self.stopCost = stopCost

    def display(self):
        print("- Vehicle : {v}".format(v=self.name))
        print("\tDepot n°{n}".format(n=self.depot.indice))
        print("\tCapacity = {c}".format(c=self.capacity))
        print("\tSpeed = {s}".format(s=self.speed))
        print("\tFixed collection time = {f}".format(f=self.fixedCollectionTime))
        print("\tCollection time per crate = {c}".format(c=self.collectionTimePerCrate))
        print("\tCosts :")
        print("\t\tFixed = {c}".format(c=self.fixedCost))
        print("\t\tPer km = {c}".format(c=self.kmCost))
        print("\t\tPer crate = {c}".format(c=self.crateCost))
        print("\t\tPer stop = {c}".format(c=self.stopCost))
