import sys
import algoGeneticAlns.run as ar

if __name__ == "__main__":
    nbGeneration = 200
    nbPopulation = 10
    if len(sys.argv) > 2:
        nbGeneration = int(sys.argv[1])
        nbPopulation = int(sys.argv[2])

    ar.solve(nbGeneration, nbPopulation)
    ar.show()
