def f(x, y, z):
    def g():
        if x < 0:
            return 1
            #return (x,y,z)
        elif x < 4:
            return 0
        elif x > 7:
            return 3
        else:
            return 2
    return g()
