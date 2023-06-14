import random
import sys
from math import floor

memoryStorage = {}


def memory(key: object, value: object = None) -> object:
    global memoryStorage
    if " " in key:
        sys.stderr.write("ERREUR : Espace interdit dans les noms de variable : " + key + "\n")
        sys.exit()
    if value is not None:
        memoryStorage[key] = value
    else:
        try:
            return memoryStorage[key]
        except:
            sys.stderr.write("ERREUR : Nom de variable inconnue : " + key)
            sys.exit()


class Dna:
    def __init__(self, gene):
        self.gene = gene
        self.fitness = 0

    def crossover(self, partner):
        gene = []
        start = floor(random.randint(0, len(self.gene) - 1))
        end = floor(random.randint(start + 1, len(self.gene)))
        for i in range(0, len(self.gene)):
            if start < i < end:
                gene.append(self.gene[i])
            else:
                gene.append(partner.gene[i])

        return gene

    def mutation(self, range):
        if random.uniform(0, 1) < range:
            print("mutation")
            i = random.randint(0, len(self.gene) - 1)
            if isinstance(memory('parametres')[i][0], int):
                self.gene[i] = random.randint(memory('parametres')[i][0], memory('parametres')[i][1])
            else:
                if isinstance(memory('parametres')[i][0], float):
                    self.gene[i] = random.uniform(memory('parametres')[i][0], memory('parametres')[i][1])
