import inspect
import imp
import logging
import os, sys
sys.path.append(os.path.abspath('pyexz3'))

# Now, we can import PyExZ3's libraries, such as...
from symbolic.loader import *
from symbolic.explore import ExplorationEngine

def sym_exec(filename, func):
    max_iters = 0
    app = loaderFactory(filename,func)
    logging.basicConfig(filename='constraints.log',level=logging.DEBUG)
    #print(("Exploring " + app.getFile() + "." + app.getEntry()))

    result = None
    try:
        engine = ExplorationEngine(app.createInvocation())
        generatedInputs, returnVals, C = engine.explore(max_iters)
    except ImportError:
        # createInvocation can raise this
        sys.exit(1)
    return (generatedInputs, returnVals, C)


def find_divergent(filename, func_name, inputs, retVals, constraints):
    '''for x in constraints:
        print(x)
        print('\n')'''
    func = None
    module = imp.load_source("__inspected__", filename)
    for x, f in inspect.getmembers(module, inspect.isfunction):
        if x == func_name:
            func = f
    if func == None:
        print("function not found in file")
        return

    args = inspect.getargspec(func)[0] # no *args or **kwargs, should not exist for global state
    vals = [0 for _ in range(len(args))]
    div_constraints = []
    for i in range(len(inputs)):
        #set up input values apropriately by matching order with function argspec
        for x, val in inputs[i]:
            for a in range(len(args)):
                if args[a] == x:
                    vals[a] = val
        if func(*vals) == retVals[i]:
            continue
        else:
            flag = 1
            #for vdict, c in constraints:
            #    for var2, val in inputs[i]:
            #        continue
                #TODO vdict[var2] is currently a symbolic integer, not concrete
            if flag:
                div_constraints.append((inputs[i], c))
    return div_constraints

# example usage
inputs, retVals, c= sym_exec('test1.py', 'f')
find_divergent('test1x.py', 'f', inputs, retVals, c)

#inputs, retVals, c = sym_exec('test1x.py', 'f')
#print(find_divergent('test1.py', 'f', inputs, retVals, c))
