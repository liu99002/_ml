from random import randint

city = [
    (0,3),(0,0),
    (0,2),(0,1),
    (1,0),(1,3),
    (2,0),(2,3),
    (3,0),(3,3),
    (3,1),(3,2)
]
citys = city

#path = [i for i in range(len(citys))]
l = len(city)
path = [(i+1)%l for i in range(l)]
# print(path)

def distance(p1, p2):
    print('p1=', p1)
    x1, y1 = p1
    x2, y2 = p2
    return ((x2-x1)**2+(y2-y1)**2)**0.5

def pathLength(p):
    dist = 0
    plen = len(p)
    for i in range(plen):
        # dist += distance(citys[p[i]], citys[p[(i+1)%plen]])
        dist += distance(city[i], city[p[i]])
    return dist

def neighbor(p):
    dx = randint(0, len(p) - 1)
    dy = randint(0, len(p) - 1)
    index1 = city.index(citys[dx])
    index2 = city.index(citys[dy])
    citys[index1], citys[index2] = citys[index2], citys[index1]
    return (citys[dx],citys[dy])

def hillClimbing(x, height, max_fail=10000):
    fail = 0
    while True:
        f1 = height
        neighbor(path)
        f2 = height

        if f2>f1:
            city = citys
            fail = 0
        else:
            fail += 1
            if fail > max_fail:
                return x


print('pathLength=', hillClimbing(0, pathLength(path)))