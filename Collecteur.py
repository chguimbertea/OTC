class Collecteur:
    INDICE = 1000

    def __init__(self, nom="collecteur", indice=None, localisation=None, capacite_depot=0, horaires=None,
                 vehicule_capacite=0, vehicule_vitesse=0, temps_collecte_fixe=0, temps_collecte_caisse=0,
                 cout_fixe=0, cout_km=0, cout_caisse=0, cout_stop=0):
        if indice is None:
            self.indice = Collecteur.INDICE
            Collecteur.INDICE += 1
        else:
            self.indice = indice

        self.nom = nom
        self.localisation = localisation
        self.capacite_depot = capacite_depot
        self.horaires = [[0, 24]] if horaires is None else horaires

        self.vehicule_capacite = vehicule_capacite
        self.vehicule_vitesse = vehicule_vitesse
        self.temps_collecte_fixe = temps_collecte_fixe
        self.temps_collecte_caisse = temps_collecte_caisse

        self.cout_fixe = cout_fixe
        self.cout_km = cout_km
        self.cout_caisse = cout_caisse
        self.cout_stop = cout_stop

    def display(self):
        print("- Collecteur n°{c} : {nom}".format(c=self.indice, nom=self.nom))
        print("\tLieu = {l}".format(l=self.localisation.to_string()))
        print("\tCapacité du dépôt = {c}".format(c=self.capacite_depot))
        print("\tCapacité du véhicule = {c}".format(c=self.vehicule_capacite))
        print("\tVitesse moyenne = {v}".format(v=self.vehicule_vitesse))
        print("\tTemps de collecte fixe = {t}".format(t=self.temps_collecte_fixe))
        print("\tTemps de collecte par caisse = {t}".format(t=self.temps_collecte_caisse))
        print("\tCoût fixe = {c}".format(c=self.cout_fixe))
        print("\tCoût par km = {c}".format(c=self.cout_km))
        print("\tCoût par caisse = {c}".format(c=self.cout_caisse))
        print("\tCoût par arrêt = {c}".format(c=self.cout_stop))
