x = 11
y = 5

def f1():
    return 42

def f2():
    global x
    x = 13
    return 43

def xert_funcs():
    return [f2]

def xert_asserts(old, new):
    assert(old.x == new.x)
