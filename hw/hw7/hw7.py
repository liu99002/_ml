from micrograd.engine import Value

x = Value(0.0)
y = Value(0.0)
z = Value(0.0)
f = x**2 + y**2 + z**2 - 2*x - 4*y - 6*z + 8

step = 0.01
for k in range(1000):
    f = x**2 + y**2 + z**2 - 2*x - 4*y - 6*z + 13
    x.grad = 0
    y.grad = 0
    z.grad = 0

    f.backward()
    print(f'\nf.data {f.data:.4f}')
    x.data -= x.grad * step
    y.data -= y.grad * step
    z.data -= z.grad * step
    print(f'x.data {x.data:.4f}') # prints 138.8338, i.e. the numerical value of dg/da
    print(f'y.data {y.data:.4f}') # prints 645.5773, i.e. the numerical value of dg/db
    print(f'z.data {z.data:.4f}') # prints 645.5773, i.e. the numerical value of dg/db
    print(f'x.grad {x.grad:.4f}') # prints 138.8338, i.e. the numerical value of dg/da
    print(f'y.grad {y.grad:.4f}') # prints 645.5773, i.e. the numerical value of dg/db
    print(f'z.grad {z.grad:.4f}') # prints 645.5773, i.e. the numerical value of dg/db
