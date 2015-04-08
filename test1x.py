def f(x, y):
    def g():
        if x < 0:
            return 1
        else:
            return 0
    return g()
