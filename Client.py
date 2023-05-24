class Client:
    def __init__(self, indice=-1, quantite=0, capacite=-1, requete=False, localisation=None, horaires=None,
                 dernier_passage=0, nom="point"):
        self.indice = indice
        self.nom = nom
        self.localisation = localisation
        self.quantite = quantite
        self.capacite = capacite
        self.requete = requete
        self.dernier_passage = dernier_passage  # Timestamp ?
        self.horaires = [[0, 24]] if horaires is None else horaires
        self.indicateurTri = 1

    def ratio(self):
        return self.quantite / self.capacite

    def priority(self):
        return (1 + self.requete) * self.ratio()

    def display(self):
        print("- Client = {c} : {nom}".format(c=self.indice, nom=self.nom))
        print("\tHoraires : {hours}".format(hours=self.horaires))
        print("\tCapacité = {c}".format(c=self.capacite))
        print("\tQuantité = {q}".format(q=self.quantite))
        print("\tRequête = {r}".format(r=self.requete))
        print("\tDernier passage = {d}".format(d=self.dernier_passage))
        print("\tPriorité = {p}".format(p=self.priority()))
        print("\tIndicateur de tri = {v}".format(v=self.indicateurTri))
