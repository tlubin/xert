import inspect
import argparse
import difflib
import random
import re

# default options that user can change
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

def run_asserts(old, new, asserts):
    def report(oldnew, x):
        # hmm... this is weird that i need these asserts to make
        # the eval call know about old and new being defined
        # looks like a bug in eval to me...will read about it :)
        assert(old) 
        assert(new) 
        print oldnew + "." + x + " = " + str(eval(oldnew + "." + x))
    passed = 1
    for myassert in asserts:
        try:
            assert(eval(myassert))
        except AssertionError:
            old_vars,new_vars = vars_of_assert(myassert)
            for x in old_vars:
                report("old", x)
            for x in new_vars:
                report("new", x)
            passed = 0
    return passed

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
            minus = (lineNum, line[2:].strip()) #saving both line number and code for now
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

def run_analysis(options, old, new, asserts):
    old_funcs = [x for _, x in inspect.getmembers(old, inspect.isfunction)]
    new_funcs = [x for _, x in inspect.getmembers(new, inspect.isfunction)]
    # TODO: constraint generation to guide this
    max_idx = len(old_funcs) - 1
    for _ in range(options['depth']):
        idx = random.randint(0, max_idx)
        print "Calling " + repr(old_funcs[idx]) # just to see what's going on
        old_funcs[idx]()
        new_funcs[idx]()
        if not run_asserts(old, new, asserts):
            break

def parse_asserts():
    # maybe get this from another file?
    # maybe get it from the source of oldfile or new file?
    asserts = ["old.x == new.x"]
    return asserts

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

def main():
    options, old, new = parse_commandline()
    asserts = parse_asserts()
    run_analysis(options, old, new, asserts)

main()
