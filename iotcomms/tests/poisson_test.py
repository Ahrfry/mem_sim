import math
import numpy as np
import matplotlib.pyplot as plt

e = 2.7182818284

def factorial(n):
    fact = 1
    for i in range(1,n+1):
        fact = fact * i
    return fact
def custom_pow(base, power):
    res = 1
    for i in range(power):
        res = res*base
    return res
def poisson(avg, k):
    l = math.pow(avg,k)
    p = math.pow(e,-avg)
    fact = factorial(k)
    return (l*p)/fact


s = np.random.poisson(100, 100)
count, bins, ignored = plt.hist(s, 14, density=True)
print(s)