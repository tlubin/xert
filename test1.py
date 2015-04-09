def f(x, y):
    def g():
        if x < 5:
            if y < 5:
                return 1
            else:
                return 2
        else:
            return 0
    return g()
