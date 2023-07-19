import alns.alnsConvertisseur as ac
import parser

if __name__ == "__main__":
    collecteur = parser.parse_collecteurs("data/Medium6/vehicule.json")[0]
    vehicle = ac.collecteurToVehicle(collecteur)
    clients = parser.parse_clients("data/Medium6/points.csv")
    nom, ntm, rtm, dtm = parser.parse_contexte("data/Medium6/contexte.json")
    instance = ac.Instance(clients, vehicle, nom)
    methode = ac.ALNS(instance, ntm, rtm, dtm)
    solution = methode.solve(withSwap=False)
    solution.display()
