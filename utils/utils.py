import geopy.distance

#top, left, right, bot = 30.2902, -97.7490, -97.7136, 30.2635 # 10 km
top, left, right, bot = 30.2858, -97.7495, -97.7255, 30.2655 # 5 km

d1 = geopy.distance.distance((top, left), (top, right))
d2 = geopy.distance.distance((top, left), (bot, left))

print('Austin')
print(d1)
print(d2)
print(float(str(d1).split(' ')[0])*float(str(d2).split(' ')[0]))

#top, left, right, bot = 41.8872, -87.6684, -87.6246, 41.8622 # 10 km
top, left, right, bot = 41.8872, -87.6517, -87.6246, 41.8663 # 5 km

d1 = geopy.distance.distance((top, left), (top, right))
d2 = geopy.distance.distance((top, left), (bot, left))

print('Chicago')
print(d1)
print(d2)
print(float(str(d1).split(' ')[0])*float(str(d2).split(' ')[0]))