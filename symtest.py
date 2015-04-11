import inspect

def f1(): pass
def f2(): pass
def f3(): pass
fs = [f1, f2, f3]

def symtest(x1, x2, x3):
    output = ''

    if x1 == 0:
        fs[0]()
        output += '0'
    elif x1 == 1:
        fs[1]()
        output += '1'
    else:
        fs[2]()
        output += '2'

    if x2 == 0:
        fs[0]()
        output += '0'
    elif x2 == 1:
        fs[1]()
        output += '1'
    else:
        fs[2]()
        output += '2'

    if x3 == 0:
        fs[0]()
        output += '0'
    elif x3 == 1:
        fs[1]()
        output += '1'
    else:
        fs[2]()
        output += '2'

    return output 
