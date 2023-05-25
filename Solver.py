class Solver:
    def __init__(self, methode):
        self.methode = methode

    def preprocess(self, list_clients, list_collecteurs):
        selection = {}
        for collecteur in list_collecteurs:
            selection[collecteur] = list_clients.copy()
        return selection

    def solve(self, list_client, collecteur):
        return self.methode.solve(list_client, collecteur)
