x = 14
y = 5

def f1():
    return 42

def f2():
    global x
    if (x == 14):
        x = 1
    return 43
