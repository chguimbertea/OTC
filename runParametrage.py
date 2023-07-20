import algoGeneticAlns.run as ar


if __name__ == "__main__":
    nbGeneration = 200
    nbPopulation = 10
    ar.solve(nbGeneration, nbPopulation)
    ar.show()
