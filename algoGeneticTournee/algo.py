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
bestFitness = 900000000
nbGeneration = 2000
nbPopulation = 1000
piscine = []
collecteur = None
matingpool = []
dict_distance = None


def map(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def setup(list_client, mycollecteur):
    global pointsDePassage, piscine, collecteur, dict_distance
    pointsDePassage = list_client
    collecteur = mycollecteur
    for i in range(0, nbPopulation):
        s = [j for j in range(0, len(pointsDePassage))]
        random.shuffle(s)
        dna = Dna(s)
        piscine.append(dna)

    tmp_list_point = list_client.copy()
    tmp_list_point.append(mycollecteur)
    dict_distance = {(i.indice, j.indice): distance(i.localisation, j.localisation, mycollecteur.vehicule_type)
                     for i in tmp_list_point for j in tmp_list_point}


def checkSolution(solution):
    global collecteur

    previousClient = pointsDePassage[solution[0]]
    passage = 60 * previousClient.horaires[0][0]
    for s in solution[1:]:
        dist = dict_distance[previousClient.indice, pointsDePassage[solution[s]].indice]
        travelTime = dist / collecteur.vehicule_vitesse * 60  # min
        collectionTime = collecteur.temps_collecte_fixe \
                         + collecteur.temps_collecte_caisse * pointsDePassage[solution[s]].quantite
        delta = passage + collectionTime + travelTime
        canPass = False
        for start, end in pointsDePassage[solution[s]].horaires:
            start = 60 * start
            end = 60 * end
            if delta <= end:
                passage = max(start, delta)
                canPass = True
                break
        if not canPass:
            return 1000
        previousClient = pointsDePassage[solution[s]]

    return 1


def calculFitness(solution):
    if not pointsDePassage:
        return 0
    else:
        dist = dict_distance[collecteur.indice, pointsDePassage[solution[0]].indice]
        for i in range(0, len(solution) - 1):
            dist += dict_distance[pointsDePassage[solution[i]].indice, pointsDePassage[solution[i + 1]].indice]
        dist += dict_distance[pointsDePassage[solution[-1]].indice, collecteur.indice]
        dist = dist * 1000  # m
        return dist * checkSolution(solution)


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
        p.fitness = map(p.fitness, minfit, maxfit, 10, 0)

    matingpool = []
    for p in piscine:
        n = p.fitness
        for i in range(0, int(n)):
            matingpool.append(p)


def selection():
    global matingpool, piscine
    newPopulation = []
    for i in range(0, nbPopulation):
        parentA = copy.deepcopy(matingpool[random.randint(0, len(matingpool) - 1)])
        parentB = copy.deepcopy(matingpool[random.randint(0, len(matingpool) - 1)])
        child = parentA.crossover(parentB)
        newPath = Dna(child)
        newPath.mutation(0.1)  # !!
        newPopulation.append(newPath)

    piscine = copy.deepcopy(newPopulation)


def run():
    global runing

    evaluation()
    selection()

    print(bestFitness, ': ', bestSolution)

    listC = []
    listLocation = [collecteur.localisation.to_tuple()]
    for p in bestSolution:
        listLocation.append(pointsDePassage[p].localisation.to_tuple())
        listC.append(pointsDePassage[p])
    listLocation.append(collecteur.localisation.to_tuple())

    previewConvexHull(listC, listLocation)

    if runing == False:
        # webbrowser.open('http://localhost:63342/rebooteille-DISP-AG/algoGeneticTournee/view.html?_ijt=oe6565he8bdsv396es0mmdgfjr&_ij_reload=RELOAD_ON_SAVE')  # Go to example.com
        webbrowser.open('file:///home/chloe/PycharmProjects/optimisationTournee/view.html')
        runing = True


def to_xy(point, r, cos_phi_0):
    lam = point[0]
    phi = point[1]
    return r * math.radians(lam) * cos_phi_0, r * math.radians(phi)


def getBestSolution():
    # depot = Client(indice=collecteur.indice, localisation=collecteur.localisation,
    #                horaires=collecteur.horaires, nom="depot_" + collecteur.nom)
    if checkSolution(bestSolution) != 1:
        return []
    solution = [collecteur]
    for s in bestSolution:
        solution.append(pointsDePassage[s])
    solution.append(collecteur)
    return solution
