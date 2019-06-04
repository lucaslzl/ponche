import geopy.distance

#top, left, right, bot = 30.2910, -97.7551, -97.7212, 30.2632
top, left, right, bot = 30.2902, -97.7490, -97.7136, 30.2635

d1 = geopy.distance.distance((top, left), (top, right))
d2 = geopy.distance.distance((top, left), (bot, left))

print('Austin')
print(d1)
print(d2)
print(float(str(d1).split(' ')[0])*float(str(d2).split(' ')[0]))

top, left, right, bot = 41.8872, -87.6684, -87.6246, 41.8622

d1 = geopy.distance.distance((top, left), (top, right))
d2 = geopy.distance.distance((top, left), (bot, left))

print('Chicago')
print(d1)
print(d2)
print(float(str(d1).split(' ')[0])*float(str(d2).split(' ')[0]))