import geopy.distance

d1 = geopy.distance.distance((41.9050, -87.6412), (41.8715, -87.6412))
d2 = geopy.distance.distance((41.9050, -87.6412), (41.9050, -87.6234))

print(d1)
print(d2)

d1 = geopy.distance.distance((43.6810, -92.9940), (43.6561, -92.9940))
d2 = geopy.distance.distance((43.6810, -92.9940), (43.6810, -92.9791))

print(d1)
print(d2)