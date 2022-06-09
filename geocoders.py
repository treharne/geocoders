import os
import requests
import time
from urllib.parse import quote

from abc import ABC, abstractmethod, abstractproperty
from dotenv import load_dotenv

load_dotenv()


class FailedGeocode(Exception):
    pass


class Geocoder(ABC):
    """
    Base class for all geocoders.
    """
    delay = 0

    @abstractmethod
    def url(self, address):
        pass

    @abstractmethod
    def result(self, response):
        pass

    @abstractmethod
    def format(self, address, result):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def wait_for_rate_limit(self):
        time.sleep(self.delay)

    def geocode(self, address):
        safe_address = quote(address, safe='')
        r = requests.get(self.url(safe_address))
        
        try:
            result = self.result(r)
        except:
            raise FailedGeocode(f'{r.status_code} {r.text} {address}')

        return self.format(address, result)


class PositionStack(Geocoder):
    key = os.getenv('KEY_POSITIONSTACK')

    def url(self, address):
        return f'http://api.positionstack.com/v1/forward?access_key={self.key}&query={address}'

    def result(self, response):
        return response.json()['data'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['label'],
            'lat': result['latitude'],
            'lon': result['longitude'],
        }


class ESRI(Geocoder):
    client_id = os.getenv('KEY_ESRI_CLIENT_ID')
    client_secret = os.getenv('KEY_ESRI_CLIENT_SECRET')
    
    def __init__(self):
        super().__init__()
        self.token = self.get_token()

    def get_token(self):
        url = 'https://www.arcgis.com/sharing/rest/oauth2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        r = requests.post(url, data=data)
        return r.json()['access_token']

    def url(self, address):
        return f'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={address}&outFields=Match_addr&maxLocations=1&f=pjson&token={self.token}'

    def result(self, response):
        return response.json()['candidates'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['address'],
            'lat': result['location']['y'],
            'lon': result['location']['x'],
        }


class Google(Geocoder):
    key = os.getenv('KEY_GOOGLE')

    def url(self, address):
        return f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.key}'

    def result(self, response):
        return response.json()['results'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['formatted_address'],
            'lat': result['geometry']['location']['lat'],
            'lon': result['geometry']['location']['lng'],
        }


class Here(Geocoder):
    key = os.getenv('KEY_HERE')

    def url(self, address):
        return f'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={self.key}'

    def result(self, response):
        return response.json()['items'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['title'],
            'lat': result['position']['lat'],
            'lon': result['position']['lng'],
        }


class OpenCage(Geocoder):
    key = os.getenv('KEY_OPENCAGE')

    def url(self, address):
        return f'https://api.opencagedata.com/geocode/v1/json?q={address}&key={self.key}'

    def result(self, response):
        return response.json()['results'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['formatted'],
            'lat': result['geometry']['lat'],
            'lon': result['geometry']['lng'],
        }


class Mapbox(Geocoder):
    key = os.getenv('KEY_MAPBOX')

    def url(self, address):
        return f'https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={self.key}'

    def result(self, response):
        return response.json()['features'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['place_name'],
            'lat': result['center'][1],
            'lon': result['center'][0],
        }


class Mapquest(Geocoder):
    key = os.getenv('KEY_MAPQUEST')

    def url(self, address):
        return f'https://www.mapquestapi.com/geocoding/v1/address?key={self.key}&location={address}'

    def result(self, response):
        return response.json()['results'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['providedLocation']['location'],
            'lat': result['locations'][0]['latLng']['lat'],
            'lon': result['locations'][0]['latLng']['lng'],
        }


class LocationIQ(Geocoder):
    key = os.getenv('KEY_LOCATIONIQ')
    delay = 1.05

    def url(self, address):
        return f'https://eu1.locationiq.com/v1/search.php?key={self.key}&q={address}&format=json'

    def result(self, response):
        return response.json()[0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['display_name'],
            'lat': float(result['lat']),
            'lon': float(result['lon']),
        }


class TomTom(Geocoder):
    key = os.getenv('KEY_TOMTOM')
    delay = 0.25

    def url(self, address):
        return f'https://api.tomtom.com/search/2/geocode/{address}.json?key={self.key}&limit=1'

    def result(self, response):
        return response.json()['results'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['address']['freeformAddress'],
            'lat': result['position']['lat'],
            'lon': result['position']['lon'],
        }


class Geoapify(Geocoder):
    key = os.getenv('KEY_GEOAPIFY')

    def url(self, address):
        return f'https://api.geoapify.com/v1/geocode/search?text={address}&format=json&apiKey={self.key}'

    def result(self, response):
        return response.json()['results'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['formatted'],
            'lat': result['lat'],
            'lon': result['lon'],
        }


class GeocodeEarth(Geocoder):
    key = os.getenv('KEY_GEOCODEEARTH')
    delay = 0.15

    def url(self, address):
        return f'https://api.geocode.earth/v1/search?text={address}&api_key={self.key}'

    def result(self, response):
        return response.json()['features'][0]

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': result['properties']['label'],
            'lat': result['geometry']['coordinates'][1],
            'lon': result['geometry']['coordinates'][0],
        }


class GeocodeXYZ(Geocoder):
    key = os.getenv('KEY_GEOCODEXYZ')
    delay = 1.5

    def url(self, address):
        return f'https://geocode.xyz/{address}?json=1&auth={self.key}'

    def result(self, response):
        j = response.json()
        assert 'longt' in j
        assert 'latt' in j
        return response.json()

    def format(self, address, result):
        return {
            'address': address,
            'geocode_address': address,
            'lat': float(result['latt']),
            'lon': float(result['longt']),
        }


class Maptiler(Geocoder):
    key = os.getenv('KEY_MAPTILER')

    def url(self, address):
        return f'https://api.maptiler.com/geocoding/{address}.json?key={self.key}'

    def result(self, response):
        return response.json()['features'][0]

    def format(self, address, result):
        print(result)
        return {
            'address': address,
            'geocode_address': address,
            'lat': result['center'][1],
            'lon': result['center'][0],
        }



geocoders = [
    cls for cls in locals().values()
    if isinstance(cls, Geocoder)
]
