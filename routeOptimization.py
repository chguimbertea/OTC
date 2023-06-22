import json
import math

import requests


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
                client.quantite
            ],
            "time_windows": tw
        }
        services.append(s)
    return services


def solve(list_client, collecteur, showLog=False):
    url = "https://graphhopper.com/api/1/vrp"
    query = {"key": "98a66451-2b12-40a8-915b-210343f0d11c"}
    headers = {"Content-Type": "application/json"}

    services = write_services(list_client, collecteur)
    start = math.floor(collecteur.horaires[0][0] * 3600)
    end = math.floor(collecteur.horaires[0][1] * 3600)

    payload = {
        "vehicles": [
            {
                "vehicle_id": collecteur.nom,
                "type_id": collecteur.vehicule_type,
                "start_address": {
                    "location_id": "depot_" + collecteur.nom,
                    "lon": collecteur.localisation.lon,
                    "lat": collecteur.localisation.lat
                },
                "earliest_start": start,
                "latest_end": end
            }
        ],
        "vehicle_types": [
            {
                "type_id": collecteur.vehicule_type,
                "capacity": [
                    collecteur.vehicule_capacite
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
                "value": "transport_time"
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

    response = requests.post(url, json=payload, headers=headers, params=query)

    if response.status_code != 200:
        print("Status : ", response.status_code)
        raise Exception(response.json()['message'])

    jdata = response.json()

    if showLog:
        with open("route.json", "w") as outfile:
            json.dump(jdata['solution'], outfile, indent=4)

        print("Distance de l'API :", jdata['solution']['routes'][0]['distance'])

    dict_client = {str(client.indice): client for client in list_client}
    data = jdata['solution']['routes'][0]['activities']
    solution = []
    for d in data:
        if d['type'] == "start" or d['type'] == "end":
            solution.append(collecteur)
        else:
            solution.append(dict_client[d['id'][2:]])

    return solution
