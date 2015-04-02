import inspect
import re
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

run_asserts()
print old_funcs[0]()
print new_funcs[0]()
