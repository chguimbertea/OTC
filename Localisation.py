from geopy.geocoders import Nominatim


class Localisation:
    def __init__(self, latitude=0, longitude=0):
        self.lat = latitude
        self.lon = longitude

    def from_DD(self, latitude, longitude):
        self.lat = latitude
        self.lon = longitude

    def from_DMS(self, degreN, minN, secN, degreE, minE, secE):
        self.lat = degreN + minN/60 + secN/3600
        self.lon = degreE + minE/60 + secE/3600

    def from_adress(self, adress):
        geocoder = Nominatim(user_agent="myGeocoder")
        loc = geocoder.geocode(adress)
        if loc is None:
            print("Adresse incorrecte : " + adress)
            return False
        self.lat = loc.latitude
        self.lon = loc.longitude
        return True

    def to_string(self):
        return "({lat}, {lon})".format(lat=self.lat, lon=self.lon)

    def display(self):
        print("Latitude : {lat}".format(lat=self.lat))
        print("Longitude : {lon}".format(lon=self.lon))
