import argparse
import sys
import traceback
import inspect
import random
import re
import ast
import xert_transform as xtr
import os

sys.path.append(os.path.abspath('codegen'))
import codegen

# default options that user can change
XASSERT = 'xert_asserts'
defaults = {
    'depth' : 10
}

def asts_to_src_str(asts):
    src = ''
    for t in asts:
        src += codegen.to_source(t) + '\n'
    return src

def asts_to_src_file(asts, filename, mode='w+'):
    src = asts_to_src_str(asts)
    f = open(filename, mode)
    f.write(src)
    f.close()

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
    xassert = None
    for x, f in inspect.getmembers(new, inspect.isfunction):
        if x == XASSERT:
            xassert = f
        else:
            new_funcs.append(f)
    if xassert == None:
        print("define xert_asserts function in new file for analysis")
        return

    # constraint generation for every changed function
    constraints = get_constraints(old_funcs, new_funcs)

    # test interleaving of functions beginning with satisfying context and patched function
    get_context(constraints)
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
def get_constraints(old_funcs, new_funcs):
    assert len(old_funcs) == len(new_funcs), "TODO: length of old and new functions should be equal"
    constraints = [[] for _ in old_funcs]
    old_transformed_asts = []
    new_transformed_asts = []
    for f in old_funcs:
        f_ast = ast.parse(inspect.getsource(f))
        old_transformed_asts.append(xtr.transform(f_ast))
    for f in new_funcs:
        f_ast = ast.parse(inspect.getsource(f))
        new_transformed_asts.append(xtr.transform(f_ast))
    tmp_dir = 'xert_tmp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    asts_to_src_file(old_transformed_asts, os.path.join(tmp_dir, '__old.py')) 
    asts_to_src_file(new_transformed_asts, os.path.join(tmp_dir, '__new.py')) 
    # TODO: call into symbolic executor with path to tmp file
    return []

def main():
    options, old, new = parse_commandline()
    run_analysis(options, old, new)

if __name__ == '__main__':
    main()
