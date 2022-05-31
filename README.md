# Comparing Geocoding APIs
We want to find the best geocoder API for our SaaS platform, [Tarot Routing](https://www.tarotanalytics.com).

Our users can upload a list of addresses interactively (e.g. from an Excel file) or via and API connection.


We have three main criteria for Geocoding APIs:
1. Quality
2. Speed
3. Price



## Quality
**Dirty Addresses**  
The addresses can be poor quality. They often:
- contain Unit numbers, Post Box numbers, Place Names, Street Corners, or even delivery instructions
- are missing the street number, or only include a postcode
- have the wrong postcode
- don't include a country or other regional identifier

**Bad Geocoders**  
Additionally, the geocode itself can be poor quality. This often happens if the geocoding provider doesn't have sufficient depth of data:
- a road doesn't exist in their map
- street numbers are not present/updated/accurate
or it does not know how to correctly interpret the address, so it ignores some of the information contained in it.

**Quality Benchmark**  
To measure quality, I've curated a list of addresses which humans can unambiguously point to on a map, but that we've seen some geocoders have problems with.

This means that each address has a corresponding *correct* lattitude and longitude.

Therefore, every time a geocoder geocodes an address, I can categorise the output as:  
> **Good**: within 100m  
> **Imprecise**: between 100m and 500m away  
> **Bad**: over 500m away  
> **Error**:  geocoder could not provide a result

These are great-circle distances measured using the [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula).


## Speed
**Volume**  
Our users often upload 50-300 addresses at a time which need to be geocoded. This geocoding happens "in real time" while they wait, so we want it to finish as fast as possible.

**Strategy**  
We send our geocoding requests asynchronously. 

This means that:
1. It's very important to understand the **Query Rate Limit** (requests/second) allowed by each Geocoder API
2. It doesn't matter *that much* how long each individual request takes.

**Speed Benchmark**  
As a result, this benchmark will geocode the addresses asynchronously.

For each geocoder, I have ignored any query rate limit listed on the website **unless my requests were throttled, in which case I send my requests at the Rate Limit**.

## Price
Different Geocoders price based on different factors
- Monthly Quantity Tiers
- Query Rate Limit
- Whether you store the lat/lon or not
- Whether it is public/private, open source, commercial, etc.

As a result, it's difficult to compare prices directly, but I will try to provide a useful, concise summary of each service's pricing.


# Pricing and Limits Summary

## [Esri](https://developers.arcgis.com/rest/geocode/api-reference/geocoding-find-address-candidates.htm)
Stored:
- US$4 per 1000 geocodes

Not Stored:
- 20k free per month
- US$0.5 per 1000 thereafter

Rate Limit: Doesn't seem to have one.

## [PositionStack](https://positionstack.com/documentation)
- 15k free per month
- US$10/mth for up to 100k
- US$50/mth for up to 1M

Rate Limit not clear, but "can be lifted" with paid plans.

## [Google Maps](https://developers.google.com/maps/documentation/geocoding)
- Free credits: $200 of usage per month
- US$5 per 1000 up to 100k/mth
- US$4 per 1000 up to 500k/mth

Rate Limit: 50 reqs/sec

## [Here Maps](https://developer.here.com/documentation/geocoding-search-api/dev_guide/topics/quick-start.html)
- Free up to 30k per month
- 0.60€ per 1000 up to 5M
- 0.48€ per 1000 up to 10M

Rate Limit: Not really clear?


## [OpenCage](https://opencagedata.com/api#quickstart)
- Free for testing, up to 1.5k req/day (but not allowed to use in prod)
- 45€ per month up to 15 req/s and 10k req/day
- 90€ per month up to 20 req/s and 20kreq/day
- Higher plans available for higher limits + rate limits
- 2 months free if you pay annually.


## [MapBox](https://docs.mapbox.com/api/search/geocoding/)
Not stored:
- Up to 100k/mth free
- US$0.75 per 1000 up to 500k
- US$0.6 per 1000 up to 1M
- etc

Stored:
- US$5 per 1000 up to 500k
- US$4 per 1000 up to 1M

Rate limit: 600 reqs/min but "can be adjusted automatically by Mapbox"


## [Mapquest](https://developer.mapquest.com/documentation/geocoding-api/)
- Free up to 15k/mth
- $99 up to 30k/mth
- $199 up to 75k/mth

Rate Limit: Doesn't appear to have a rate limit


## [LocationIQ](https://locationiq.com/geocoding)
- Free: 5k req/day and 2 req/sec
- US$49: 10k req/day and 15 req/sec
- US$99: 25k req/day and 20 req/sec
- etc

50% discount for startups under 2yrs
Enforces rate limit from the first second!

## [TomTom](https://developer.tomtom.com/search-api/documentation/geocoding-service/geocode)
- Free: 2.5k req/day. Explicitly allows commercial applications
- US$0.50 per 1000 reqs after 2.5k/day.

Rate Limit: 5 req/sec -> enforced immediately.


# [GeocodeEarth](https://geocode.earth/)
- 14 Day Free Trial: 1k reqs, 10 reqs/sec
- US$100: 150k reqs/mth, 10 reqs/sec
- US$200: 400k reqs/mth, 10 reqs/sec
- etc

Rate Limit enforced immediately.


## [Geocodio](https://www.geocod.io/)
- US and Canada Only


## [Geoapify](https://www.geoapify.com/geocoding-api)
- Free: 3k reqs/day, 5 reqs/sec, explicitly includes commercial
- 49€: 10k reqs/day, 12 reqs/sec
- 89€: 25k reqs/day, 15 reqs/sec
- etc

"In general, we do not throttle if you go over the limits"


## [Geocode.xyz](https://geocode.xyz/api)
- Free for less than 1 req/sec **across all of their users**
- $2.5 per 1000 reqs, 10 reqs/sec
- $200 for unlimited, 10 reqs/sec
- can buy multiple "unlimited" plans to increase query rate

They also have [an AMI](https://aws.amazon.com/marketplace/pp/prodview-oyheuvytbpoiu#pdp-overview) that you can launch (and pay them for) on your own account.

## [Maptiler](https://docs.maptiler.com/cloud/api/#tag/Geocoding)
- Free: 100k/mth, non commercial
- $25: 500k/mth then US$0.10 per 1000
- $295: 5M/mth then $0.08 per 1000

No apparent rate limit
