import copy
import math
import random
import webbrowser

from algoGeneticTournee.dna import Dna
from methodes import distance
from preview import previewConvexHull

runing = False
pointsDePassage = []
bestSolution = []
bestFitness = 999999999999
nbPopulation = 1000
tauxMutation = 0.1
piscine = []
collecteur = None
matingpool = []
dict_distance = None


def map(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def setup(list_client, my_collecteur, nb_pop=1000, taux_mut=0.05):
    global pointsDePassage, piscine, collecteur, dict_distance, nbPopulation, tauxMutation
    pointsDePassage = list_client
    collecteur = my_collecteur
    nbPopulation = nb_pop
    tauxMutation = taux_mut
    for i in range(0, nbPopulation):
        s = [j for j in range(0, len(pointsDePassage))]
        random.shuffle(s)
        dna = Dna(s)
        piscine.append(dna)

    tmp_list_point = list_client.copy()
    tmp_list_point.append(collecteur)
    dict_distance = {(i.indice, j.indice): distance(i.localisation, j.localisation, collecteur.vehicule_type)
                     for i in tmp_list_point for j in tmp_list_point}


def checkSolution(solution):
    global collecteur

    previousClient = collecteur
    passage = 60 * previousClient.horaires[0][0]
    # Vérification du passage pour chaque point
    for s in solution:
        dist = dict_distance[previousClient.indice, pointsDePassage[s].indice]
        travelTime = dist / collecteur.vehicule_vitesse * 60  # min
        collectionTime = collecteur.temps_collecte_fixe \
                         + collecteur.temps_collecte_caisse * pointsDePassage[s].quantite
        delta = passage + collectionTime + travelTime
        canPass = False
        for start, end in pointsDePassage[s].horaires:
            start = 60 * start  # min
            end = 60 * end  # min
            if delta <= end:
                passage = max(start, delta)
                canPass = True
                break
        if not canPass:
            return 1000
        previousClient = pointsDePassage[s]

    # Vérification de l'arrivée au dépôt
    dist = dict_distance[previousClient.indice, collecteur.indice]
    travelTime = dist / collecteur.vehicule_vitesse * 60  # min
    delta = passage + travelTime
    canPass = False
    for start, end in collecteur.horaires:
        end = 60 * end  # min
        if delta <= end:
            canPass = True
            break
    if not canPass:
        return 1000
    return 1


def calculFitness(solution):
    if not pointsDePassage:
        return 0
    else:
        dist = dict_distance[collecteur.indice, pointsDePassage[solution[0]].indice]
        for i in range(0, len(solution) - 1):
            dist += dict_distance[pointsDePassage[solution[i]].indice, pointsDePassage[solution[i + 1]].indice]
        dist += dict_distance[pointsDePassage[solution[-1]].indice, collecteur.indice]
        # dist en km
        return pow(dist * checkSolution(solution), 4)


def evaluation():
    global piscine, bestSolution, matingpool, bestFitness

    for p in piscine:
        p.fitness = calculFitness(p.gene)

    indexBest = -1
    minfit = piscine[0].fitness
    maxfit = piscine[0].fitness
    for i, p in enumerate(piscine):
        if p.fitness < minfit:
            minfit = p.fitness

        if p.fitness > maxfit:
            maxfit = p.fitness

        if p.fitness <= bestFitness:
            indexBest = i
            bestFitness = p.fitness

    if indexBest >= 0:
        bestSolution = piscine[indexBest].gene

    for p in piscine:
        if minfit == maxfit:
            f = 5
        else:
            f = map(p.fitness, minfit, maxfit, 10, 0)
        p.fitness = f

    matingpool = []
    for p in piscine:
        n = p.fitness
        for i in range(0, int(n)):
            matingpool.append(p)


def selection():
    global matingpool, piscine, tauxMutation
    newPopulation = []
    for i in range(0, nbPopulation):
        parentA = copy.deepcopy(matingpool[random.randint(0, len(matingpool) - 1)])
        parentB = copy.deepcopy(matingpool[random.randint(0, len(matingpool) - 1)])
        child = parentA.crossover(parentB)
        newPath = Dna(child)
        newPath.mutation(tauxMutation)
        newPopulation.append(newPath)

    piscine = copy.deepcopy(newPopulation)


def run(showLog=False):
    global runing

    evaluation()
    selection()

    if showLog:
        print(bestFitness, ': ', bestSolution)

        listC = []
        listLocation = [collecteur.localisation.to_tuple()]
        for p in bestSolution:
            listLocation.append(pointsDePassage[p].localisation.to_tuple())
            listC.append(pointsDePassage[p])
        listLocation.append(collecteur.localisation.to_tuple())

        previewConvexHull(listC, listLocation)

        if runing == False:
            # CHANGE THE PATH
            webbrowser.open('file:///home/chloe/PycharmProjects/optimisationTournee/view.html')
            runing = True


def getBestSolution():
    if checkSolution(bestSolution) != 1:
        return []
    solution = [collecteur]
    for s in bestSolution:
        solution.append(pointsDePassage[s])
    solution.append(collecteur)
    return solution
