a = 0
b = 0

def f1():
    global a
    a+=1

def f2():
    global b
    b+=1

def f3():
    global a
    a-=1

f2()
f3()
print a
