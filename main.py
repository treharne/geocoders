import csv
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import haversine
from geocoders import geocoders, FailedGeocode
from tabulate import tabulate


if __name__ == '__main__':

    with open('data/addresses.csv') as f:
        reader = csv.DictReader(f)
        location_map = {row['address']: {'lat': float(row['lat']), 'lon': float(row['lon'])} for row in reader}
        addresses = list(location_map.keys())

    # for address in addresses:
    #     parsed_address = libpostal.parse(address)
    #     pprint.pprint(parsed_address)

    summaries = []

    for geocoder in geocoders:

        with ThreadPoolExecutor(max_workers=20) as executor:
            start = time.time()
            futures = []
            for address in addresses:
                f = executor.submit(geocoder.geocode, address)
                futures.append(f)
                geocoder.wait_for_rate_limit()

            tally = Counter()
            geocoded = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    geocoded.append(result)
                except FailedGeocode as e:
                    print(f'{geocoder.name} failed: {e}')
                    tally['error'] += 1

            duration = round(time.time() - start, 1)

        for geocoded_location in geocoded:
            actual_location = location_map[geocoded_location['address']]
            kilometres = round(haversine.dist(geocoded_location, actual_location), 1)
            if kilometres > 0.5:
                tally['bad'] += 1
                print(f'{geocoder.name} bad geocode {kilometres}km for {geocoded_location["address"]}')
            elif kilometres > 0.1:
                tally['imprecise'] += 1
                print(f'{geocoder.name} imprecise geocode {kilometres}km for {geocoded_location["address"]}')
            else:
                tally['good'] += 1

        summaries.append({
            'Geocoder': geocoder.name,
            'Duration': f'{duration}s',
            'Good': tally['good'],
            'Imprecise': tally['imprecise'],
            'Bad': tally['bad'],
            'Error': tally['error'],
        })
    
    sorted_summaries = sorted(summaries, key=lambda x: x['Good'], reverse=True)
    print(tabulate(sorted_summaries, headers='keys', tablefmt='presto'))
    # for geocoder_func in geocoders:
    #     geocoder_name = geocoder_func.__name__
        
    #     summary = summaries[geocoder_name]['tally']

    #     print()
    #     print(f'{geocoder_name}')
    #     # print(f'{summary['duration']} seconds, {summary["good"]} good, {summary["imprecise"]} imprecise, {summary["bad"]} bad, {summary["error"]} error')
    #     t = tabulate()



