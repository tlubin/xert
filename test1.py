from symbolic.args import *

def f(x, y, z):
    def g():
        if x < 0:
            return 1
            #return (x,y,z)
        else:
            return 0
            #global x
            #x = x + 1
            #return (x, y, z)
    return g()
