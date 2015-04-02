a = 0
b = 0

def f1():
    global a
    a+=1

def f2():
    global b
    #patch here
    b+=2

def f3():
    global a
    a-=1

f2()
f3()
print a
