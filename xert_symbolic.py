import inspect
import imp
import logging
import old
import new
import os, sys
sys.path.append(os.path.abspath('pyexz3'))

# Now, we can import PyExZ3's libraries, such as...
from symbolic.loader import *
from symbolic.explore import ExplorationEngine

def sym_exec(filename, func):
    max_iters = 0
    app = loaderFactory(filename,func)
    logging.basicConfig(filename='constraints.log',level=logging.DEBUG)
    print(("Exploring " + app.getFile() + "." + app.getEntry()))

    result = None
    try:
        engine = ExplorationEngine(app.createInvocation())
        generatedInputs, returnVals, path = engine.explore(max_iters)
    except ImportError:
        # createInvocation can raise this
        sys.exit(1)
    return (generatedInputs, returnVals, path)

inputs, retVals, path = sym_exec('xert_explore.py', 'sym_explore')
