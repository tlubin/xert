x = 14
y = 5

def f1():
    return 42

def f2():
    global x
    if (x == 14):
        x = 0
    return 43

def xert_asserts(old, new):
    assert(old.x == new.x)
