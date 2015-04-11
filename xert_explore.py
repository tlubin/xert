import old
import new
import inspect
import random

def sym_explore(function):
    XASSERT = 'xert_asserts'
    old_funcs = [f for _, f in inspect.getmembers(old, inspect.isfunction)]
    new_funcs = []
    xassert = None
    for x, f in inspect.getmembers(new, inspect.isfunction):
        if x == XASSERT:
            xassert = f
        else:
            new_funcs.append(f)
    if xassert == None:
        print("define xert_asserts function in new file for analysis")
    for i in range(len(old_funcs)):
        if function == i:
            old_funcs[function]()
            new_funcs[function]()
            if (xassert(old, new)):
                sym_explore(function)
            else:
                print("xassert FAILED")
                return 1


