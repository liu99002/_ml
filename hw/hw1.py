import random

# def hillClimbing(f, x, y, z, h=0.01):
#     failCount = 0                    # 失敗次數歸零
#     while (failCount < 10000):       # 如果失敗次數小於一萬次就繼續執行
#         fxyz = f(x, y, z)                # fxy 為目前高度
#         dx = random.uniform(-h, h)   # dx 為左右偏移量
#         dy = random.uniform(-h, h)   # dy 為前後偏移量
#         dz = random.uniform(-h, h)
#         if f(x+dx, y+dy, z+dz) <= fxyz:     # 如果移動後高度比現在高
#             x = x + dx               #   就移過去
#             y = y + dy
#             z = z + dz
#             print('x={:.3f} y={:.3f} z={:.3f} f(x,y,z)={:.3f}'.format(x, y, z, fxyz))
#             failCount = 0            # 失敗次數歸零
#         else:                        # 若沒有更高
#             failCount = failCount + 1#   那就又失敗一次
#     return (x,y,fxyz)                 # 結束傳回 （已經失敗超過一萬次了）

def hillClimbing(f, x, y, z, h=0.01):
    while (True):
        fxyz = f(x, y, z)
        print('x={0:.3f} y={1:.3f} z={2:.3f} f(x,y,z)={3:.3f}'.format(x, y, z, fxyz))
        if f(x+h, y, z) <= fxyz:
            x = x + h
        elif f(x-h, y, z) <= fxyz:
            x = x - h
        elif f(x, y+h, z) <= fxyz:
            y = y + h
        elif f(x, y-h, z) <= fxyz:
            y = y - h
        elif f(x, y, z+h) <= fxyz:
            z = z + h
        elif f(x, y, z-h) <= fxyz:
            z = z - h
        else:
            break
    return (x,y,z,fxyz)

def f(x, y, z):
    return x**2 + y**2 + z**2 - 2*x - 4*y - 6*z + 8
hillClimbing(f, 0, 0, 0)
