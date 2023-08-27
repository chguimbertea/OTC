# Optimisation de Tournée de Collecte 
Projet de stage de Master 2 sur l'optimisation des tournées de véhicules 
appliquées à la collecte de bouteilles en verre consignées

Dernière mise-à-jour le : [2023-08-27]

**Statut** : en développement

## Installation
- [ ] rédiger les explications de configurations

## Utilisation

#### Partie ALNS
L'algorithme ALNS résout un problème de tournée multi-route 
avec les points dans le fichier "points.csv",
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

#### Partie parametrage de l'ALNS
Le paramétrage des paramètres de l'ALNS permet de fixer les 4 paramètres non fixés par la littérature. 
L'algorithme génétique situé dans le module **algoGeneticAlns** est utilise les données du dossier "dataBase" et 
produit un fichier "gene.csv" contenant le meilleur gene de chaque génération.

Par défaut, nous avons 200 générations et une population de taille 10.
> python3 runParametrage.py {nbGeneration} {nbPopulation}

