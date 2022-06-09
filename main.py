from copy import deepcopy
import csv
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import haversine
from geocoders import geocoders, FailedGeocode
from tabulate import tabulate


def load_address_data():
    with open('data/addresses.csv') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    for row in data:
        row['lat'] = float(row['lat'])
        row['lon'] = float(row['lon'])

    return data


def geocode_addresses(address_data, geocoder, n_workers=20):
    addresses = [row['address'] for row in address_data]

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        start = time.time()
        futures = []
        for row in address_data:
            address = row['address']
            f = executor.submit(geocoder.geocode, address)
            futures.append(f)
            geocoder.wait_for_rate_limit()

        output = deepcopy(address_data)
        for future, row in zip(futures, output):
            try:
                row['result'] = future.result()
            except FailedGeocode as e:
                row['result'] = None
                print(f'{geocoder.name} failed: {e}')

    return {
        'output': output,
        'duration': round(time.time() - start, 1)
    }


def load_existing_benchmark():
    try:
        with open('data/results.json', 'r') as f:
            benchmark = json.load(f)
    except FileNotFoundError:
        benchmark = {}
    return benchmark


def evaluate_geocode_quality(geocoder_benchmark):
    counts = Counter()
    for loc in geocoder_benchmark['output']:
        actual = loc
        geocoded = loc['result']

        if not geocoded:
            counts['error'] += 1
            continue

        kilometres = round(haversine.dist(actual, geocoded), 1)
        geocoded['dist_from_actual'] = kilometres

        if kilometres > 0.5:
            counts['bad'] += 1
        elif kilometres > 0.1:
            counts['imprecise'] += 1
        else:
            counts['good'] += 1


    return counts


def make_summary(name, geocoder_benchmark):
    quality = geocoder_benchmark['quality']
    return {
        'Geocoder': name,
        'Duration': f'{geocoder_benchmark["duration"]}s',
        'Good': quality['good'],
        'Imprecise': quality['imprecise'],
        'Bad': quality['bad'],
        'Error': quality['error'],
    }


def format_output_table(benchmark):
    summaries = [
        make_summary(name, geocoder_benchmark)
        for name, geocoder_benchmark in benchmark.items()
    ]

    sorted_summaries = sorted(summaries, key=lambda x: x['Good'], reverse=True)
    return tabulate(sorted_summaries, headers='keys', tablefmt='presto')

def update_readme(summary_table):
    with open('README.md', 'r') as f:
        lines = [line for line in f.read().splitlines()]
    
    start_idx = None
    end_idx = None
    for idx, line in enumerate(lines):
        if not start_idx:
            if line.startswith('# Results'):
                start_idx = idx
                continue
            else:
                continue
        
        if line.startswith('# Criteria'):
            end_idx = idx
            break

    if not end_idx:
        raise Exception('Cannot update readme without matching headings')

    before = lines[:start_idx]
    after = lines[end_idx:]

    results_section = [
        '# Results',
        '',
        '```json',
        summary_table,
        '```'
        '',
        'Detailed results available in [results.json](data/results.json)',
        '',
    ]

    updated_readme = '\n'.join(before + results_section + after)

    with open('README.md', 'w') as f:
        f.write(updated_readme)

def save(benchmark):
    with open('data/results.json', 'w') as f:
        json.dump(benchmark, f, indent=2)

if __name__ == '__main__':
    address_data = load_address_data()

    existing_benchmark = load_existing_benchmark()

    benchmark = {}
    for Geocoder in geocoders:
        if Geocoder.name in existing_benchmark:
            continue
        benchmark[Geocoder.name] = geocode_addresses(address_data, Geocoder())

    benchmark.update(existing_benchmark)

    save(benchmark)
    
    for geocoder_name, geocoder_benchmark in benchmark.items():
        geocoder_benchmark['quality'] = evaluate_geocode_quality(geocoder_benchmark)

    save(benchmark)

    summary_table = format_output_table(benchmark)
    update_readme(summary_table)
 
