import csv
import json
import pprint
import requests

libpostal_url = 'http://localhost:8080/parser'

def parse(address):
    '''
    Make a request to Libpostal (running locally) to split the 
    address into fields.
    '''
    r = requests.post(libpostal_url, json={'query': address})
    return {
        entry['label']: entry['value']
        for entry in r.json()
    }


if __name__ == '__main__':
    with open('data/addresses.csv') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    all_keys = set()
    for row in data:
        address = row['address']
        parsed = parse(address)
        row['parsed'] = parsed

        row['lat'] = float(row['lat'])
        row['lon'] = float(row['lon'])
        
        all_keys |= set(parsed.keys())

    with open('data/addresses.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(all_keys)
