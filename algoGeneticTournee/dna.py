import random
from math import floor
from methodes import distance


class Dna:
    def __init__(self, gene=[]):
        self.gene = gene
        self.fitness = None

    def crossover(self, partner):
        gene = []
        start = floor(random.randint(0, len(self.gene) - 1))
        end = floor(random.randint(start + 1, len(self.gene)))
        for i in range(start, end):
            gene.append(self.gene[i])

        for i in partner.gene:
            if i not in gene:
                gene.append(i)
        return gene

    def mutation(self, range):
        if random.uniform(0, 1) < range:
            i = random.randint(0, len(self.gene) - 1)
            j = random.randint(0, len(self.gene) - 1)
            c = self.gene[i]
            self.gene[i] = self.gene[j]
            self.gene[j] = c
