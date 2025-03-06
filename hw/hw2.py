from random import randint

city = [
    (0,3),(0,0),
    (0,2),(0,1),
    (1,0),(1,3),
    (2,0),(2,3),
    (3,0),(3,3),
    (3,1),(3,2)
]

cities = city.copy()

l = len(city)
path = [(i+1)%l for i in range(l)]

def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x2-x1)**2+(y2-y1)**2)**0.5

def pathLength(arr):
    dist = 0
    plen = len(path)
    for i in range(plen):
        dist += distance(arr[i], arr[path[i]])
    return round(dist, 2)

def neighbor():
    dx = randint(0, len(path) - 1)
    dy = randint(0, len(path) - 1)
    t = cities[dx]
    cities[dx] = cities[dy]
    cities[dy] = t
    return pathLength(cities)

def hillClimbing(x, arr, max_fail=10000):
    fail = 0
    while True:
        f1 = pathLength(arr)
        f2 = neighbor()

        if f2 > f1:
            fail += 1
            if fail > max_fail:
                return x, arr
        else:
            fail = 0
            arr = cities.copy()
            x = f2
            print(f'f1 = {f1} f2 = {f2} fail = {fail} ')
        

print('pathLength=', hillClimbing(0, city))