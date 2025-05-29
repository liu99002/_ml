import torch
import math

dtype = torch.float
x = torch.randn((), dtype=dtype, requires_grad=True)
y = torch.randn((), dtype=dtype, requires_grad=True)
z = torch.randn((), dtype=dtype, requires_grad=True)

def loss_fn(x):
	loss = x**2 + y**2 + z**2 - 2*x - 4*y - 6*z + 8
	return loss

def GD(x, y, z, loss_fn, loop_max = 10000, learning_rate = 1e-3):
	for t in range(loop_max):
		loss = loss_fn(x)
		if t % 100 == 99:
			print(f'Result: x = {x.item()} y = {y.item()} z = {z.item()} loss={loss_fn(x)}')
		loss.backward()
		with torch.no_grad():
			x -= learning_rate * x.grad
			x.grad = None
			y -= learning_rate * y.grad
			y.grad = None
			z -= learning_rate * z.grad
			z.grad = None

GD(x, y, z, loss_fn, loop_max = 5000)

print(f'Result: x = {x.item()} y = {y.item()} z = {z.item()} loss={loss_fn(x)}')