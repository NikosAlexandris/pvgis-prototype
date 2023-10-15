import numpy as np
from scipy.optimize import minimize

# Define the function to be optimized (negative of a Gaussian distribution)
def f(x):
    return -np.exp(-x**2)

# Initial guess
x0 = 2.0

# Print the initial guess and its corresponding function value
print(f"Initial guess: x = {x0}, f(x) = {f(x0)}")

# Define a callback function to print the optimization process
def callback(x):
    print(f"Current guess: x = {x}, f(x) = {f(x)}")

# Optimize the function
res = minimize(f, x0, method='Nelder-Mead', callback=callback)

# Print the result
print(f"\nOptimized result: x = {res.x}, f(x) = {f(res.x)}")
