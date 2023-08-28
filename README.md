# Optimisation de Tournée de Collecte 
Projet de stage de Master 2 sur l'optimisation des tournées de véhicules 
appliquées à la collecte de bouteilles en verre consignées

Dernière mise-à-jour le : [2023-08-27]

**Statut** : en développement

## Installation
- [ ] faire la liste des besoins pour le bon fonctionnement du code

## Utilisation

### Bloc ALNS
L'algorithme ALNS, contenu dans le module **alns**, résout un problème de tournée 
multi-route avec les points dans le fichier "points.csv",
le véhicule contenu dans le fichier "vehicule.json"
et les éléments extérieur dans le fichier "contexte.json".
Ces fichiers doivent être dans un même dossier passé en argument *{filePath}*.
Par défaut ce dossier est "dataBase".

La solution retournée est un ensemble de périodes (timeslot) contenant des routes 
qui elles-même sont une liste ordonnées de points définissant le chemin à prendre.

L'objectif est par défaut le calcul initial du travail précédent. 
Il peut être remplacé par la minimisation de la distance ou de la durée 
en changeant l'argument correspondant par le mot clé souhaité parmi
"cost", "distance" et "duration".
> python3 runBase.py {filePath} {objectif}

### Bloc parametrage de l'ALNS
Le paramétrage des paramètres de l'ALNS permet de fixer les 4 paramètres non fixés par la littérature. 
L'algorithme génétique situé dans le module **algoGeneticAlns** est utilise les données du dossier "dataBase" et 
produit un fichier "gene.csv" contenant le meilleur gene de chaque génération.

Par défaut, nous avons 200 générations et une population de taille 10.
> python3 runParametrage.py {nbGeneration} {nbPopulation}

### Bloc algorithmes d'optimisation de tournées
#### PLNE
Le module **plne** contient l'implémentation d'un programme linéaire en nombre entier d'un VRPTW
qui utilise la bibliothèque Python-MIP.
Le temps limite d'exécution est posé à 3600s.

#### Algorithme génétique
Le module **algoGeneticTournee** contient les fichiers de code d'un algorithme génétique pour optimiser une tournée 
de véhicules. Par défaut, l'algorithme utilise 10 générations, une population de 1000 et un taux de mutation de 0,1. 
Vous pouvez ajuster ces paramètres selon vos besoins. 
De plus, le chemin d'accès du fichier de sortie graphique est à modifier dans le fichier "algo.py", 
en suivant l'exemple 'file:///home/chloe/PycharmProjects/optimisationTournee/view.html'. 

#### API Routing Optimization
Le module **apiRO** est conçu pour utiliser l'API d'optimisation de tournée de GraphHopper. 
GraphHopper est un service qui fournit des API pour le routage, l'optimisation de tournée, la géocodage, 
et d'autres fonctionnalités liées à la géolocalisation. Pour utiliser ce module, vous aurez besoin d'une clé API de 
GraphHopper, car elle est nécessaire pour effectuer des requêtes à l'API d'optimisation de tournée. 
Assurez-vous d'obtenir une clé API valide de GraphHopper et de la configurer correctement dans le fichier 
"routOptimization.py" et "methodes.py" afin d'utiliser les services de GraphHopper.

#### Comparaison
L'exécutable "runComparaison.py" permet de comparer quatre méthodes d'optimisation de tournée : 
le programme linéaire, l'algorithme ALNS, l'algorithme génétique et l'API de GraphHopper. 
Chaque méthode prend en paramètre la liste des points à visiter et le collecteur qui effectue la tournée. 
Les résultats de la comparaison sont enregistrés dans le fichier "comparaison.csv", ce qui facilite l'analyse 
des performances de chaque méthode et aide à choisir la plus appropriée pour votre application.
> python3 runComparaison.py

Chaque méthode peut également être exécutée individuellement dans l'exécutable "main.py".

## Affichage

**preview()** : affichage d'une solution sous forme de liste

**previewSolution()** : affichage d'une instance de la classe Solution

**previewConvexHull()** : affichage de l'étape intermédiaire metant en avant les points sélectionnés,
l'enveloppe convexe et les points internes sur l'ensemble des points

**previewSelection()** : affichage d'une sélection de points sous forme de dictionnaire