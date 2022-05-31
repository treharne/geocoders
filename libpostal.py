import requests

def parse(address):
    r = requests.post('http://localhost:8080/parser', json={'query': address})
    return r.json()
    