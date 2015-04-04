x = 14
y = 5

def f1():
    return 42

def f2():
    global x
    if (x == 14):
        x = 0
    return 43

def xert_funcs(old, new):
    old = [old.f2]
    new = [new.f2]
    return (old, new)

def xert_asserts(old, new):
    assert(old.x == new.x)
