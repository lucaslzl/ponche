import geopy.distance

d1 = geopy.distance.distance((30.2822, -97.7472), (30.2822, -97.7369))
d2 = geopy.distance.distance((30.2822, -97.7472), (30.2651, -97.7472))

print('Austin')
print(d1)
print(d2)

d1 = geopy.distance.distance((41.8962, -87.6359), (41.8962, -87.6257))
d2 = geopy.distance.distance((41.8962, -87.6359), (41.8779, -87.6359))

print('Chicago')
print(d1)
print(d2)