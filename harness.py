import inspect
import random
import re
import difflib
import sys
import old
import new

old_funcs = [x for _, x in inspect.getmembers(old, inspect.isfunction)]
new_funcs = [x for _, x in inspect.getmembers(new, inspect.isfunction)]

myassert = "old.x == new.x"
old_re = "old.\w+" # this is not comprehensive...
new_re = "new.\w+" # this is not comprehensive...
old_vars = []
new_vars = []
for m in re.findall(old_re, myassert):
    old_vars.append(m.split(".")[1])
for m in re.findall(new_re, myassert):
    new_vars.append(m.split(".")[1])

def run_asserts():
    try:
        assert(eval(myassert))
    except AssertionError:
        for x,y in zip(old_vars, new_vars):
            print "old." + x + " = " + str(eval("old." + x))
            print "new." + y + " = " + str(eval("new." + y))
        return False
    return True

max_idx = len(old_funcs) - 1
for _ in range(10):
    idx = random.randint(0, max_idx)
    print "Calling " + repr(old_funcs[idx]) # just to see what's going on
    old_funcs[idx]()
    new_funcs[idx]()
    if not run_asserts():
       break

def find_xlines():
    oldtxt = open('old.py').readlines()
    newtxt = open('new.py').readlines()
    changes = []

    d = difflib.Differ()
    diffs = d.compare(oldtxt, newtxt)
    lineNum = 0
    minus = None

    for line in diffs:
        code = line[:2]
        if minus and code != "? ":
            changes.append(minus)
        minus = None
        if code in ("  ", "- "):
            lineNum += 1
        if code == "- ":
            minus = (lineNum, line[2:].strip())
        if code == "+ ":
            changes.append((lineNum, line[2:].strip()))
    return changes

def find_functions():
    funcs = []
    for (ln, _) in find_xlines():
        for i in range(len(old_funcs)):
            source = inspect.getsourcelines(old_funcs[i])
            if ln >= source[1] and ln <= source[1] + len(source[0])-1:
                funcs.append(old_funcs[i])
    return funcs
