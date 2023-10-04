import math
import requests
import geopy.distance as gd

# key = "98a66451-2b12-40a8-915b-210343f0d11c"
key = "0046f82f-a3f3-4503-a204-1f9519bdae8f"
cpt = 0  # compteur du nombre d'appels à la fonction distance


def distance(locI, locJ, mode=None):
    """
    mode = None, la valeur de la distance retournée est calculée à vol d'oiseau
    mode = value, la valeur de la distance retournée est exacte en tenant compte le chemin emprunté
    """
    global cpt, key
    cpt += 1
    mode = None
    if mode:
        r = requests.get("https://graphhopper.com/api/1/route?point=" + locI.to_url() + "&point=" + locJ.to_url()
                         + "&profile=" + mode + "&locale=en&calc_points=false&key=" + key)
        if r.status_code == 200:
            return r.json()['paths'][0]['distance'] / 1000  # km
        else:
            print("Status : ", r.status_code)
            raise Exception(r.json()['message'])
    else:
        return gd.geodesic(locI.to_tuple(), locJ.to_tuple()).km


def get_path_details(startLat, startLon, endLat, endLon, mode):
    r = requests.get("https://graphhopper.com/api/1/route?point=" + str(startLat) + "," + str(startLon)
                     + "&point=" + str(endLat) + "," + str(endLon) + "&profile=" + mode
                     + "&locale=en&calc_points=true&points_encoded=false&key=98a66451-2b12-40a8-915b-210343f0d11c")
    if r.status_code == 200:
        line = r.json()['paths'][0]['points']['coordinates']
        route = []
        for i in line:
            route.append((i[1], i[0]))
        return route
    else:
        print("Status : ", r.status_code)
        raise Exception(r.json()['message'])


def fitness_single_routing(solution, collecteur, list_client):
    # INITIALISATION
    quantiteTotale = 0
    distanceTotale = 0
    dureeTotale = 0
    notInRoute = {client.indice: 1 for client in list_client}

    if solution:
        clientDepart = collecteur
        clientArrivee = solution[0]
        dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
        distanceTotale += dist
        dureeTotale += dist / collecteur.vehicule_vitesse * 60

        for i in range(1, len(solution)):
            clientDepart = clientArrivee
            clientArrivee = solution[i]

            if clientArrivee.indice < 1000:
                # QUANTITE
                quantiteTotale += clientArrivee.quantite

                # DUREE en min
                dureeTotale += dist / collecteur.vehicule_vitesse * 60
                dureeTotale += collecteur.temps_collecte_fixe + collecteur.temps_collecte_caisse * clientArrivee.quantite

            # DISTANCE
            dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
            distanceTotale += dist

            # PRESENCE
            notInRoute[clientArrivee.indice] = 0

        clientDepart = clientArrivee
        clientArrivee = collecteur
        dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
        distanceTotale += dist
        dureeTotale += dist / collecteur.vehicule_vitesse * 60

    # TAUX DE REMPLISSAGE
    remplissage = collecteur.vehicule_capacite / max(1, quantiteTotale)

    # COUT D'UTILISATION
    cout = collecteur.cout_fixe
    cout += (1 + collecteur.cout_km) * distanceTotale
    cout += collecteur.cout_caisse * quantiteTotale
    cout += collecteur.cout_stop * (len(solution) - 2)

    # SATISFACTION
    satisfaction = 0
    for client in list_client:
        satisfaction += client.priorite() * notInRoute[client.indice]

    return pow(satisfaction, 4) + pow(remplissage, 4) + pow(cout, 4)


def fitness_multiple_routing(solution, list_client):
    fitness = 0
    notInRoute = {client.indice: 1 for client in list_client}

    for collecteur, sol in solution.items():
        if not sol:
            continue

        quantiteTotale = 0
        dureeTotale = 0

        clientDepart = collecteur
        clientArrivee = sol[0]
        dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
        dureeTotale += dist / collecteur.vehicule_vitesse * 60

        for i in range(1, len(sol)):
            clientDepart = clientArrivee
            clientArrivee = sol[i]

            # DISTANCE
            dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)

            # DUREE en min
            dureeTotale += dist / collecteur.vehicule_vitesse * 60
            dureeTotale += collecteur.temps_collecte_fixe + collecteur.temps_collecte_caisse * clientArrivee.quantite

            # Si le client n'est pas un dépôt
            if clientArrivee.indice < 999:
                # QUANTITE
                quantiteTotale += clientArrivee.quantite

                # PRESENCE
                notInRoute[clientArrivee.indice] = 0

        clientDepart = clientArrivee
        clientArrivee = collecteur
        dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
        dureeTotale += dist / collecteur.vehicule_vitesse * 60

        # INVERSE TAUX DE REMPLISSAGE
        remplissage = collecteur.vehicule_capacite / max(1, quantiteTotale)

        fitness += remplissage + dureeTotale

    # SATISFACTION
    satisfaction = 0
    for client in list_client:
        satisfaction += client.priorite() * notInRoute[client.indice]

    fitness += satisfaction

    return fitness


def remove_farthest_client(listClient, collecteur):
    if not listClient:
        return None
    maxId = -1
    maxDist = 0
    for i, client in enumerate(listClient):
        dist = distance(collecteur.localisation, client.localisation, collecteur.vehicule_type)
        if dist >= maxDist:
            maxId = i
            maxDist = dist
    if maxId == -1:
        raise Exception("No farthest client")
    return listClient.pop(maxId)


def nearest_point(mypoint, points):
    if not points:
        return None
    bestPoint = points[0]
    minDist = 999999999
    for point in points:
        dist = distance(mypoint.localisation, point.localisation)/point.vehicule_vitesse
        if dist < minDist:
            bestPoint = point
            minDist = dist
    return bestPoint


def leftmost_client(listClient):
    leftmostClient = listClient[0]
    for client in listClient:
        if (client.localisation.to_tuple()[1] < leftmostClient.localisation.to_tuple()[1]) or (
                client.localisation.to_tuple()[1] == leftmostClient.localisation.to_tuple()[1] and
                client.localisation.to_tuple()[0] <= leftmostClient.localisation.to_tuple()[0]):
            leftmostClient = client
    return leftmostClient


# CONVEX HULL
def determinant(u, v):
    return u[0] * v[1] - u[1] * v[0]


def vecteur(A, B):
    return B[0] - A[0], B[1] - A[1]


def pseudo_angle(A, B, C):
    u = vecteur(A, B)
    v = vecteur(A, C)
    return determinant(u, v)


def compare(A, B, C, mode):
    t = pseudo_angle(A.localisation.to_tuple(), B.localisation.to_tuple(), C.localisation.to_tuple())
    if t > 0:
        return True
    elif t < 0:
        return False
    else:
        return distance(A.localisation, B.localisation, mode) <= distance(A.localisation, C.localisation, mode)


def convexHull(listClient, mode):
    clientHull = [leftmost_client(listClient)]

    candidat = listClient[0]
    for client in listClient:
        if compare(clientHull[-1], candidat, client, mode):
            candidat = client
    clientHull.append(candidat)
    listClient.remove(clientHull[-1])

    while clientHull[-1] != clientHull[0] and listClient:
        candidat = listClient[0]
        for client in listClient:
            if compare(clientHull[-1], candidat, client, mode):
                candidat = client
        clientHull.append(candidat)
        listClient.remove(clientHull[-1])
    return [client.localisation.to_tuple() for client in clientHull]


# INSIDE POINTS
def intersect(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # parallel
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    if ua < 0 or ua > 1:  # out of range
        return None
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ub < 0 or ub > 1:  # out of range
        return None
    x = x1 + ua * (x2 - x1)
    y = y1 + ua * (y2 - y1)
    return x, y


def is_inside(listPoint, focalPoint, point):
    nbIntersec = 0
    for i in range(len(listPoint)):
        if intersect(listPoint[i], listPoint[i - 1], focalPoint, point) is not None:
            nbIntersec += 1
    return nbIntersec % 2 == 1


def inside_intersection(listClientDispo, listConvexHull, focalPoint, residualQuantity):
    result = []
    for client in listClientDispo:
        if 0 < client.quantite <= residualQuantity:
            if is_inside(listConvexHull, focalPoint, client.localisation.to_tuple()):
                result.append(client)
    return result


def angle(A, B, C):
    if A == B or A == C or B == C:
        return 360  # !! vérifier en amont la suppression correcte des points
    u = vecteur(A, B)
    v = vecteur(A, C)
    scalar = u[0] * v[0] + u[1] * v[1]
    normeU = u[0] * u[0] + u[1] * u[1]
    normeV = v[0] * v[0] + v[1] * v[1]
    racine = math.sqrt(normeU * normeV)
    rad = math.acos(scalar / racine)
    return math.degrees(rad)


def inside_near_points(listClientDispo, solution, residualQuantity):
    ANGLE = 160
    result = []
    if not solution:
        return result
    for client in listClientDispo:
        if 0 < client.quantite <= residualQuantity:
            previousClient = solution[0]
            for nextClient in solution[1:]:
                A = previousClient.localisation.to_tuple()
                B = nextClient.localisation.to_tuple()
                theta = angle(client.localisation.to_tuple(), A, B)
                if ANGLE < theta < 360 - ANGLE:
                    result.append(client)
                    break
                previousClient = nextClient

    return result
