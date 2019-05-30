import geopy.distance

d1 = geopy.distance.distance((30.2889, -97.7615), (30.2889, -97.7375))
d2 = geopy.distance.distance((30.2889, -97.7615), (30.2704, -97.7615))

print('Austin')
print(d1)
print(d2)

d1 = geopy.distance.distance((41.8873, -87.6493), (41.8873, -87.6232))
d2 = geopy.distance.distance((41.8873, -87.6493), (41.8667, -87.6493))

print('Chicago')
print(d1)
print(d2)