from collections import deque
from matplotlib import pyplot as plt
import pandas as pd
import alns.alnsConvertisseur as ac

from algoGeneticAlns import algo
from parser import parse_collecteurs, parse_clients


def solve(nbGeneration=100, nbPopulation=10, fileName="./algoGeneticAlns/gene.csv"):
    collecteur = parse_collecteurs("data/Medium6/vehicule.json")[0]
    vehicule = ac.collecteurToVehicle(collecteur)
    clients = parse_clients("data/Medium6/points.csv")
    instance = ac.Instance(clients, vehicule)
    methode = ac.ALNS(instance)

    algo.setup(methode, nbPopulation, fileName)
    for i in range(nbGeneration):
        algo.run()


def show(fileName='algoGeneticAlns/gene.csv'):
    rho = deque(maxlen=200)
    dmax = deque(maxlen=200)
    theta = deque(maxlen=200)
    ns = deque(maxlen=200)
    f = []

    df = pd.read_csv(fileName, delimiter=';', index_col=False)
    for index, row in df.iterrows():
        rho.append(row['rho'])
        dmax.append(row['dmax'])
        theta.append(row['theta'])
        ns.append(row['Ns'])
        f.append(row['Fitness'])

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("itération")
    ax1.set_ylabel("valeur")

    ax1.plot(rho, label='rho')
    ax1.scatter(range(len(rho)), rho)

    ax1.plot(dmax, label='dmax')
    ax1.scatter(range(len(dmax)), dmax)

    ax1.plot(theta, label='theta')
    ax1.scatter(range(len(theta)), theta)

    ax1.plot(ns, label='ns')
    ax1.scatter(range(len(ns)), ns)

    ax1.legend(loc="upper right")

    # Échelle fitness
    # for i, v in enumerate(f):
    #     f[i] = v * 1

    ax2 = ax1.twinx()
    color = 'tab:purple'
    ax2.set_ylabel('fitness', color=color)
    ax2.plot(f, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.show()
