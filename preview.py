import webbrowser

import folium
from methodes import get_path_details

RADIUS = 3
COLORS = ['red', 'blue', 'purple', 'orange', 'green', 'gray', 'darkblue', 'darkred', 'darkgreen', 'cadetblue']
ANCRE = (45.760266, 4.849236)


def preview(solution, collecteur, list_clients=None, filename="routing"):
    routing = folium.Map(location=ANCRE, zoom_start=10)

    # Clients
    list_clients = [] if list_clients is None else list_clients
    for client in list_clients:
        folium.CircleMarker(location=client.localisation.to_tuple(), popup=client.nom, radius=RADIUS).add_to(routing)

    idColor = 0
    clientsLocation = []
    depot_is_drawing = False
    for s in solution:
        if not clientsLocation:
            clientsLocation.append(s.localisation.to_tuple())
        else:
            start = clientsLocation.pop()
            clientsLocation += get_path_details(start[0], start[1], s.localisation.lat, s.localisation.lon,
                                                collecteur.vehicule_type)

        idColor = idColor % len(COLORS)

        if s.indice == collecteur.indice:
            if depot_is_drawing:
                folium.PolyLine(clientsLocation, color=COLORS[idColor]).add_to(routing)
                clientsLocation = []
                idColor += 1
            else:
                folium.Marker(s.localisation.to_tuple(), popup=s.nom,
                              icon=folium.Icon(icon='warehouse', prefix='fa')).add_to(routing)
                depot_is_drawing = True
        else:
            folium.Marker(s.localisation.to_tuple(), popup=s.nom,
                          icon=folium.Icon(color=COLORS[idColor], icon='boxes-stacked', prefix='fa')).add_to(routing)

    name = "{name}.html".format(name=filename)
    routing.save(name)
    print(name + " has been saved")
    webbrowser.open('file:///home/chloe/PycharmProjects/optimisationTournee/' + name)


def previewSolution(solution, filename=None):
    routing = folium.Map(location=ANCRE, zoom_start=10)

    # Clients
    for client in solution.instance.listClient:
        folium.CircleMarker(location=client.localisation.to_tuple(), popup=client.nom, radius=RADIUS).add_to(routing)

    idColor = 0
    for timeslot in solution.listTimeSlot:
        for route in timeslot.listRoute:
            if len(route.trajet) == 0:
                continue

            idColor = idColor % len(COLORS)

            # Depot
            depot = route.trajet[0]
            folium.Marker(depot.localisation.to_tuple(), popup=depot.nom,
                          icon=folium.Icon(color=COLORS[idColor], icon='warehouse', prefix='fa')).add_to(routing)

            # Routing
            clientsLocation = []
            for client in route.trajet:
                clientsLocation.append(client.localisation.to_tuple())
                if client.indice < 999:
                    folium.Marker(client.localisation.to_tuple(), popup=client.indice,
                                  icon=folium.Icon(color=COLORS[idColor], icon='boxes-stacked', prefix='fa')).add_to(
                        routing)
            folium.PolyLine(clientsLocation, color=COLORS[idColor]).add_to(routing)

            idColor += 1

    filename = solution.instance.name if filename is None else filename
    name = "{name}.html".format(name=filename)
    routing.save(name)
    print(name + " has been saved")


def previewConvexHull(listSelectedClient, listConvexHullPoint=None, listClientInside=None, listAllClient=None,
                      focalPoint=None, filename="view", showLog=False):
    if listConvexHullPoint is None:
        listConvexHullPoint = []
    if listClientInside is None:
        listClientInside = []
    if listAllClient is None:
        listAllClient = []

    if showLog:
        print("nbr de clients au total = {n}".format(n=len(listAllClient)))
        print("nbr de clients selectionnnés = {n}".format(n=len(listSelectedClient)))
        print("nbr de clients definissant l'enveloppe = {n}".format(n=len(listConvexHullPoint) - 1))
        print("nbr de clients à l'intérieur = {n}".format(n=len(listClientInside)))

    selectedColor = 'red'
    convexHullColor = 'black'
    insideColor = 'purple'
    allColor = 'blue'
    view = folium.Map(location=ANCRE, zoom_start=11)

    if focalPoint is not None:
        folium.Marker(focalPoint, popup='focal', icon=folium.Icon(color='black')).add_to(view)
    for point in listAllClient:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.indice, color=allColor,
                            radius=RADIUS).add_to(view)
    for point in listClientInside:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.indice, color=insideColor,
                            radius=RADIUS).add_to(view)
    for point in listSelectedClient:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.indice, color=selectedColor,
                            radius=RADIUS).add_to(view)
        if showLog:
            folium.Marker(point.localisation.to_tuple(), popup=point.nom,
                          icon=folium.Icon(color=selectedColor, icon='boxes-stacked', prefix='fa')).add_to(view)
    if listConvexHullPoint:
        folium.PolyLine(listConvexHullPoint, color=convexHullColor).add_to(view)

    name = "{name}.html".format(name=filename)
    view.save(name)
    print(name + " has been saved")


def previewSelection(solution, clients=None, filename="selection"):
    map = folium.Map(location=ANCRE, zoom_start=10)

    if clients is None:
        clients = []
    for client in clients:
        folium.CircleMarker(location=client.localisation.to_tuple(), popup=client.nom,
                            radius=2, color='black').add_to(map)

    idColor = 0
    for collecteur in solution.keys():
        idColor = idColor % len(COLORS)
        # DEPOT
        folium.Marker(collecteur.localisation.to_tuple(), popup=collecteur.nom,
                      icon=folium.Icon(color=COLORS[idColor], icon='warehouse', prefix='fa')).add_to(map)

        # POINT
        for point in solution[collecteur]:
            for j in range(0, int(point.quantite), 2):
                folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.nom,
                                    radius=2*(j+1), color=COLORS[idColor]).add_to(map)
            line = [point.localisation.to_tuple(), collecteur.localisation.to_tuple()]
            folium.PolyLine(line, color=COLORS[idColor]).add_to(map)

        idColor += 1

    name = "{name}.html".format(name=filename)
    map.save(name)
    print(name + " has been saved")
