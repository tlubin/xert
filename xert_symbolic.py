import inspect
import imp
import os, sys
sys.path.append(os.path.abspath('pyexz3'))

# Now, we can import PyExZ3's libraries, such as...
from symbolic.loader import *
from symbolic.explore import ExplorationEngine

def sym_exec(filename, func):
    max_iters = 0
    solver = "z3"
    app = loaderFactory(filename,func)
    print(("Exploring " + app.getFile() + "." + app.getEntry()))

    result = None
    try:
        engine = ExplorationEngine(app.createInvocation(), solver=solver)
        generatedInputs, returnVals, path = engine.explore(max_iters)
    except ImportError:
        # createInvocation can raise this
        sys.exit(1)
    return (generatedInputs, returnVals, path)


def find_divergent(filename, func_name, inputs, retVals, path):
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
            #TODO find constraints by traversing path and add to div_constraints
            div_constraints.append(0)
    return div_constraints

# example usage
inputs, retVals, path = sym_exec('test1.py', 'f')
find_divergent('test1x.py', 'f', inputs, retVals, path)

inputs, retVals, path = sym_exec('test1x.py', 'f')
find_divergent('test1.py', 'f', inputs, retVals, path)
