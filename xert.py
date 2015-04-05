import argparse
import sys
import traceback
import inspect
import random
import re

# default options that user can change
XERT = 'xert_asserts'
XFUNCS = 'xert_funcs'
defaults = {
    'depth' : 10
}

def vars_of_assert(myassert):
    old_re = "old.\w+" # this is not right...e.g. old.0
    new_re = "new.\w+"
    old_vars = []
    new_vars = []
    for m in re.findall(old_re, myassert):
        old_vars.append(m.split(".")[1])
    for m in re.findall(new_re, myassert):
        new_vars.append(m.split(".")[1])
    return old_vars, new_vars

# it would be nice to be able to dump ALL the state,
# unsure how to get all global variables using inspect...
# so for now parse the failed assert to get the touched variables
def dump_state(old, new, text):
    old_vars, new_vars = vars_of_assert(text)
    for x in old_vars:
        print('old.{} = {}'.format(x, old.x))
    for x in new_vars:
        print('new.{} = {}'.format(x, new.x))

def run_analysis(options, old, new):
    # get old/new functions and cross-asserts
    old_funcs = [f for _, f in inspect.getmembers(old, inspect.isfunction)]
    new_funcs = []
    xfuncs = []
    xassert = None
    for x, f in inspect.getmembers(new, inspect.isfunction):
        if x == XERT:
            xassert = f
        elif x == XFUNCS:
            xfuncs = f(old, new)
        else:
            new_funcs.append(f)
    if xassert == None:
        print("define xert_asserts function in new file for analysis")
        return
    if len(xfuncs) < 1:
        print("define xert_funcs function in new file for analysis")
        return

    # constraint generation for every changed function
    constraints = [[] for _ in range (len(xfuncs[0]))]
    for i in range(len(xfuncs[0])):
        constraints[i] = get_constraints(xfuncs[0][i], xfuncs[1][i])

    # test interleaving of functions beginning with satisfying context and patched function
    get_context(constraints[0])
    #TODO use context to start interleaving of functions
    max_idx = len(old_funcs) - 1
    for _ in range(options['depth']):
        idx = random.randint(0, max_idx)
        print("Calling " + repr(old_funcs[idx])) # just to see what's going on
        # TODO: also check return value?? let user assert things about returns...
        old_funcs[idx]()
        new_funcs[idx]()
        try:
            xassert(old, new)
        except AssertionError:
            print("xassert FAILED")
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)
            tb_info = traceback.extract_tb(tb)
            text = tb_info[-1][-1]
            dump_state(old, new, text)
            exit(1)

def parse_commandline():
    p = argparse.ArgumentParser()
    p.add_argument('oldfile', help='The original python file (without .py)')
    p.add_argument('newfile', help='The new python file (without .py)')
    p.add_argument('--depth', help='Maximum depth of function calls', type=int)
    args = p.parse_args()
    options = defaults
    for k, v in vars(args).iteritems():
        if v:
            options[k] = v
    old = __import__(options['oldfile'])
    new = __import__(options['newfile'])
    return options, old, new

#TODO get interleaving of function calls to satisfy given constraint set
def get_context(c):
    #run some function interleaving
    #after each function runs, test the following on the state of "new"
    satisfied = 1
    for constraint in c:
        try:
            assert constraint
        except AssertionError:
            satisfied = 0
            break
    if satisfied:
        #return satisfying function interleaving
        return 1
    else:
        #try a different function interleaving or continue this one
        return 0

#TODO generate the set of constraints necessary to get different outcome from patch
def get_constraints(oldf, newf):
    #some symbolic execution magic here
    return []

def main():
    options, old, new = parse_commandline()
    run_analysis(options, old, new)
main()
