import copy
import random
from algoGeneticAlns.dna import Dna, memory


def map(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def setup(method, pop_size=10, fileName="./algoGeneticAlns/gene.csv"):
    print("Setup START---------")

    memory('alns', method)
    memory('parametres', [])
    memory('file', open(fileName, "w+"))
    memory('file').write('rho;dmax;theta;Ns;Fitness\n')
    memory("metaParametres", [])
    memory("metaParametresNb", 4)
    memory("metaParametresHistorique", [])

    memory("bestFitness", 89999999999999999999999999)
    memory("bestMetaParametres", [])

    memory("popSize", pop_size)
    memory("population", [])
    memory("matingpool", [])

    # bornes min/max pour mutation
    memory('parametres').append((0.1, 0.5))  # rho
    memory('parametres').append((0.2, 0.9))  # dMax
    memory('parametres').append((0.1, 1.0))  # theta
    memory('parametres').append((1, 20))  # nbSwap

    for j in range(0, memory("popSize")):
        gene = list(range(0, 4))
        # gene = [0.3, 0.2, 0.5, 10]
        for i in range(4):
            if isinstance(memory('parametres')[i][0], int):
                gene[i] = random.randint(memory('parametres')[i][0], memory('parametres')[i][1])
            else:
                if isinstance(memory('parametres')[i][0], float):
                    gene[i] = random.uniform(memory('parametres')[i][0], memory('parametres')[i][1])

        memory("population").append(Dna(gene))

    print("Setup END-----------")


def calculateFitness(gene):
    meanCost = 0
    meanTime = 0
    for i in range(5):
        solution = memory("alns").solve(rho=gene[0], dMax=gene[1], theta=gene[2], nbSwap=gene[3], withSwap=True)
        meanCost += solution.getCost()
        meanTime += solution.totalTime
    meanCost = meanCost/5
    meanTime = meanTime/5
    print("cost² :", pow(meanCost, 2), "time² :", pow(meanTime, 2))
    return pow(meanCost, 2) + pow(meanTime, 2)


def evaluate():
    for p in memory("population"):
        p.fitness = calculateFitness(p.gene)

    indexBest = -1
    minfit = memory("population")[0].fitness
    maxfit = memory("population")[0].fitness

    for i, p in enumerate(memory("population")):
        if p.fitness <= minfit:
            minfit = p.fitness
            indexBest = i

        if p.fitness > maxfit:
            maxfit = p.fitness

    if indexBest >= 0:
        memory("bestMetaParametres", memory("population")[indexBest].gene)
        memory("bestFitness", memory("population")[indexBest].fitness)
        memory("metaParametresHistorique").append(memory("population")[indexBest].gene)
        memory('file').write(str(memory("population")[indexBest].gene[0]) + ";")
        memory('file').write(str(memory("population")[indexBest].gene[1]) + ";")
        memory('file').write(str(memory("population")[indexBest].gene[2]) + ";")
        memory('file').write(str(memory("population")[indexBest].gene[3]) + ";")
        memory('file').write(str(minfit) + ";\n")

    for p in memory("population"):
        if minfit == maxfit:
            f = 0.5
        else:
            f = map(p.fitness, minfit, maxfit, 1, 0)
        p.fitness = f

    memory("matingpool", [])
    for p in memory('population'):
        n = p.fitness * 10
        for i in range(0, int(n) + 1):
            memory("matingpool").append(p)


def selection():
    newPopulation = []
    for i in range(0, memory("popSize")):
        parentA = copy.deepcopy(memory("matingpool")[random.randint(0, len(memory("matingpool")) - 1)])
        parentB = copy.deepcopy(memory("matingpool")[random.randint(0, len(memory("matingpool")) - 1)])
        child = parentA.crossover(parentB)
        newPath = Dna(child)
        newPath.mutation(0.1)
        newPopulation.append(newPath)

    memory('population', newPopulation)


def run():
    evaluate()
    selection()
    print(memory("bestFitness"), ':', memory("bestMetaParametres"))
    print("meta", memory("metaParametresHistorique"))
