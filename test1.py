def f(x, y):
    def g():
        if x < 1:
            if y < 1:
                return 1
            else:
                return 2
        else:
            return 0
    return g()
