from Localisation import Localisation


class Client:
    def __init__(self, indice=-1, quantite=0, capacite=-1, requete=False, localisation=Localisation(), horaires=None,
                 jours_depuis_collecte=0, qualite_tri=0, collecteurs_disponibles=None, nom="point"):
        self.indice = indice
        self.nom = nom
        self.localisation = localisation
        self.quantite = quantite
        self.capacite = capacite
        self.requete = requete
        self.jours_depuis_collecte = jours_depuis_collecte
        self.horaires = [[0, 24*7]] if horaires is None else horaires  # h

        if collecteurs_disponibles is None:
            collecteurs_disponibles = []
        if qualite_tri == -1:
            collecteurs_disponibles = collecteurs_disponibles[::-1]
        self.collecteurs_disponibles = collecteurs_disponibles

        self.visite = False

    def ratio(self):
        return self.quantite / self.capacite

    def priorite(self):
        # return (1 + self.requete) * self.ratio()
        if self.quantite == 0 or self.jours_depuis_collecte == 0:
            return 0
        if self.jours_depuis_collecte != 0:
            vitesse_remplissage = max(0.1, self.jours_depuis_collecte * (self.capacite / self.quantite - 1))
            return (1 + self.requete) / vitesse_remplissage

    def display(self):
        print("- Client = {c} : {nom}".format(c=self.indice, nom=self.nom))
        print("\tLieu : {l}".format(l=self.localisation.to_tuple()))
        print("\tHoraires : {hours}".format(hours=self.horaires))
        print("\tCapacité = {c}".format(c=self.capacite))
        print("\tQuantité = {q}".format(q=self.quantite))
        print("\tRequête = {r}".format(r=self.requete))
        print("\tNbr de jours depuis dernière collecte = {d}".format(d=self.jours_depuis_collecte))
        print("\tPriorité = {p}".format(p=self.priorite()))
        print("\tCollecteurs disponibles = {c}".format(c=self.collecteurs_disponibles))
