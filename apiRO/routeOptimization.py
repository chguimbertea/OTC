import json
import math
import requests

# key = "98a66451-2b12-40a8-915b-210343f0d11c"
key = "0046f82f-a3f3-4503-a204-1f9519bdae8f"


def write_time_windows(horaires):
    tw = []
    for h in horaires:
        tw.append({
            "earliest": math.floor(3600 * h[0]),
            "latest": math.floor(3600 * h[1])
        })
    return tw


def write_services(list_client, collecteur):
    services = []
    for client in list_client:
        d = math.floor(60 * (collecteur.temps_collecte_fixe + collecteur.temps_collecte_caisse * client.quantite))
        tw = write_time_windows(client.horaires)
        s = {
            "id": "s-" + str(client.indice),
            "name": client.nom,
            "type": "pickup",
            "address": {
                "location_id": "l-" + str(client.indice),
                "lon": client.localisation.lon,
                "lat": client.localisation.lat
            },
            "duration": d,
            "size": [
                int(client.quantite)
            ],
            "time_windows": tw
        }
        services.append(s)
    return services


def write_vehicles(collecteur):
    vehicles = []
    for j, h in enumerate(collecteur.horaires):
        start = math.floor(h[0] * 3600)
        end = math.floor(h[1] * 3600)
        v = {
                "vehicle_id": collecteur.nom+"-"+str(j+1),
                "type_id": collecteur.vehicule_type,
                "start_address": {
                    "location_id": "depot_" + collecteur.nom,
                    "lon": collecteur.localisation.lon,
                    "lat": collecteur.localisation.lat
                },
                "earliest_start": start,
                "latest_end": end
            }
        vehicles.append(v)
    return vehicles


def solve(list_client, collecteur, showLog=False):
    url = "https://graphhopper.com/api/1/vrp"
    query = {"key": key}
    headers = {"Content-Type": "application/json"}

    services = write_services(list_client, collecteur)

    payload = {
        "vehicles": write_vehicles(collecteur),
        "vehicle_types": [
            {
                "type_id": collecteur.vehicule_type,
                "capacity": [
                    int(collecteur.vehicule_capacite)
                ],
                "profile": collecteur.vehicule_type,
                "speed_factor": 0.9
            }
        ],
        "services": services,
        "shipments": [],
        "objectives": [
            {
                "type": "min",
                "value": "completion_time"
                # completion_time pour ajouter les temps d'attente
                # transport_time pour seulement les temps de trajet
            }
        ],
        "configuration": {
            "routing": {
                "calc_points": False,
                "snap_preventions": [
                    "motorway",
                    "trunk",
                    "tunnel",
                    "bridge",
                    "ferry"
                ]
            }
        }
    }

    if showLog:
        with open("input.json", "w") as outfile:
            json.dump(payload, outfile, indent=4)

    response = requests.post(url, json=payload, headers=headers, params=query)

    if response.status_code != 200:
        print("Status : ", response.status_code)
        raise Exception(response.json()['message'])

    jdata = response.json()

    if showLog or True:
        with open("output.json", "w") as outfile:
            json.dump(jdata['solution'], outfile, indent=4)

    dict_client = {str(client.indice): client for client in list_client}
    solution = []
    temps = -1
    if len(jdata['solution']['routes']):
        data = jdata['solution']['routes'][0]['activities']
        temps = jdata['solution']['routes'][0]['completion_time']
        for d in data:
            if d['type'] == "start" or d['type'] == "end":
                solution.append(collecteur)
            else:
                solution.append(dict_client[d['id'][2:]])

    return solution
    # return solution, temps
