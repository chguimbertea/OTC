import math
import requests
import geopy.distance as gd

key = "98a66451-2b12-40a8-915b-210343f0d11c"
cpt = 0


def distance(locI, locJ, mode):
    global cpt, key
    cpt += 1
    key = None  # !!
    if key:
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
        for l in line:
            route.append((l[1], l[0]))
        return route
    else:
        print("Status : ", r.status_code)
        raise Exception(r.json()['message'])


def fitness(solution, collecteur, list_client):
    # INITIALISATION
    quantiteTotale = 0
    distanceTotale = 0
    dureeTotale = 0
    notInRoute = {client.indice: 1 for client in list_client}

    clientArrivee = solution[0]
    for i in range(1, len(solution)):
        clientDepart = clientArrivee
        clientArrivee = solution[i]

        # QUANTITE
        quantiteTotale += clientArrivee.quantite

        # DISTANCE
        dist = distance(clientDepart.localisation, clientArrivee.localisation, collecteur.vehicule_type)
        distanceTotale += dist

        # DUREE en min
        dureeTotale += dist / collecteur.vehicule_vitesse * 60
        dureeTotale += collecteur.temps_collecte_fixe + collecteur.temps_collecte_caisse * clientArrivee.quantite

        # PRESENCE
        notInRoute[clientArrivee.indice] = 0

    # TAUX DE REMPLISSAGE
    remplissage = collecteur.vehicule_capacite / max(1, quantiteTotale)

    # COUT D'UTILISATION
    cout = collecteur.cout_fixe \
           + (1 + collecteur.cout_km) * distanceTotale \
           + collecteur.cout_caisse * quantiteTotale \
           + collecteur.cout_stop * (len(solution) - 2)

    # SATISFACTION
    satisfaction = 0
    for client in list_client:
        satisfaction += client.priorite() * notInRoute[client.indice]

    return pow(satisfaction, 8) + pow(remplissage, 4) + pow(cout, 4)


def farthest_id_client(listClient, collecteur):
    maxIdClient = -1
    maxDist = 0
    for client in listClient:
        dist = distance(collecteur.localisation, client.localisation, collecteur.vehicule_type)
        if dist > maxDist:
            maxIdClient = client.indice
            maxDist = dist
    return maxIdClient


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
