import folium

RADIUS = 3


def preview(solution, filename=None):
    colors = ['red', 'blue', 'purple', 'orange', 'green', 'gray', 'darkblue', 'darkred', 'darkgreen', 'cadetblue']
    routing = folium.Map(location=(45.760266, 4.849236), zoom_start=10)

    # Clients
    for client in solution.instance.listClient:
        folium.CircleMarker(location=client.localisation.to_tuple(), popup=client.nom, radius=RADIUS).add_to(routing)

    idColor = 0
    for timeslot in solution.listTimeSlot:
        for route in timeslot.listRoute:
            if len(route.trajet) == 0:
                continue

            idColor = idColor % len(colors)

            # Depot
            depot = route.trajet[0]
            folium.Marker(depot.localisation.to_tuple(), popup=depot.name,
                          icon=folium.Icon(color=colors[idColor], icon='warehouse', prefix='fa')).add_to(routing)

            # Routing
            clientsLocation = []
            for client in route.trajet:
                clientsLocation.append(client.localisation.to_tuple())
                if client.indice < 999:
                    folium.Marker(client.localisation.to_tuple(), popup=client.indice,
                                  icon=folium.Icon(color=colors[idColor], icon='boxes-stacked', prefix='fa')).add_to(
                        routing)
            folium.PolyLine(clientsLocation, color=colors[idColor]).add_to(routing)

            idColor += 1

    filename = solution.instance.name if filename is None else filename
    name = "{name}.html".format(name=filename)
    routing.save(name)
    print(name + " has been saved")


def previewConvexHull(listSelectedClient, listConvexHullPoint=None, listClientInside=None, listAllClient=None,
                      focalPoint=None, filename=None):
    if listConvexHullPoint is None:
        listConvexHullPoint = []
    if listClientInside is None:
        listClientInside = []
    if listAllClient is None:
        listAllClient = []

    print("nbr de clients au total = {n}".format(n=len(listAllClient)))
    print("nbr de clients selectionnnés = {n}".format(n=len(listSelectedClient)))
    print("nbr de clients definissant l'enveloppe = {n}".format(n=len(listConvexHullPoint) - 1))
    print("nbr de clients à l'intérieur = {n}".format(n=len(listClientInside)))

    selectedColor = 'red'
    convexHullColor = 'black'
    insideColor = 'purple'
    allColor = 'blue'
    view = folium.Map(location=(45.760266, 4.849236), zoom_start=11)

    if focalPoint is not None:
        folium.Marker(focalPoint, popup='focal', icon=folium.Icon(color='black')).add_to(view)
    for point in listAllClient:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.name, color=allColor, radius=RADIUS).add_to(view)
    for point in listClientInside:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.name, color=insideColor, radius=RADIUS).add_to(view)
    for point in listSelectedClient:
        folium.CircleMarker(location=point.localisation.to_tuple(), popup=point.name, color=selectedColor, radius=RADIUS).add_to(view)
        folium.Marker(point.localisation.to_tuple(), popup=point.indice,
                      icon=folium.Icon(color=selectedColor, icon='boxes-stacked', prefix='fa')).add_to(view)
    if listConvexHullPoint:
        folium.PolyLine(listConvexHullPoint, color=convexHullColor).add_to(view)

    filename = "view" if filename is None else filename
    name = "{name}.html".format(name=filename)
    view.save(name)
    print(name + " has been saved")
