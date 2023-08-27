class Collecteur:
    INDICE = 1000

    def __init__(self, nom="collecteur", indice=None, localisation=None, horaires=None,
                 vehicule_capacite=0, vehicule_vitesse=0, temps_collecte_fixe=0, temps_collecte_caisse=0,
                 cout_fixe=0, cout_km=0, cout_caisse=0, cout_stop=0):
        if indice is None:
            self.indice = Collecteur.INDICE
            Collecteur.INDICE += 1
        else:
            self.indice = indice

        self.nom = nom
        self.localisation = localisation
        self.horaires = [[0, 24*7]] if horaires is None else horaires  # h

        self.vehicule_capacite = vehicule_capacite
        self.vehicule_vitesse = vehicule_vitesse  # km/h
        if 25 < vehicule_vitesse:
            self.vehicule_type = "car"
        else:
            self.vehicule_type = "bike"
        self.temps_collecte_fixe = temps_collecte_fixe  # min
        self.temps_collecte_caisse = temps_collecte_caisse  # min

        self.cout_fixe = cout_fixe
        self.cout_km = cout_km
        self.cout_caisse = cout_caisse
        self.cout_stop = cout_stop

    def display(self):
        print("- Collecteur n°{c} : {nom}".format(c=self.indice, nom=self.nom))
        print("\tLieu = {l}".format(l=self.localisation.to_string()))
        print("\tHoraires = {h}".format(h=self.horaires))
        print("\tCapacité du véhicule = {c}".format(c=self.vehicule_capacite))
        print("\tVitesse moyenne = {v}".format(v=self.vehicule_vitesse))
        print("\tTemps de collecte fixe = {t}".format(t=self.temps_collecte_fixe))
        print("\tTemps de collecte par caisse = {t}".format(t=self.temps_collecte_caisse))
        print("\tCoût fixe = {c}".format(c=self.cout_fixe))
        print("\tCoût par km = {c}".format(c=self.cout_km))
        print("\tCoût par caisse = {c}".format(c=self.cout_caisse))
        print("\tCoût par arrêt = {c}".format(c=self.cout_stop))
