import inspect
import argparse
import sys
import traceback
import difflib
import random
import re

# default options that user can change
XERT = 'xert_asserts'
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
        print 'old.{} = {}'.format(x, old.x)
    for x in new_vars:
        print 'new.{} = {}'.format(x, new.x)

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
            changes.append(minus) #ensure save deleted line of code
        minus = None
        if code in ("  ", "+ "):
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

def run_analysis(options, old, new):
    old_funcs = [f for _, f in inspect.getmembers(old, inspect.isfunction)]
    new_funcs = [f for x, f in inspect.getmembers(new, inspect.isfunction) if x != XERT]
    xassert = [f for x, f in inspect.getmembers(new, inspect.isfunction) if x == XERT]
    if len(xassert) != 1:
        print "define xassert function in new file for analysis"
        return
    else:
        xassert = xassert[0]
    # TODO: constraint generation to guide this
    max_idx = len(old_funcs) - 1
    for _ in range(options['depth']):
        idx = random.randint(0, max_idx)
        print "Calling " + repr(old_funcs[idx]) # just to see what's going on
        # TODO: also check return value?? let user assert things about returns...
        old_funcs[idx]()
        new_funcs[idx]()
        try:
            xassert(old, new)
        except AssertionError:
            print "xassert FAILED"
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

def main():
    options, old, new = parse_commandline()
    run_analysis(options, old, new)
    find_xlines()
main()
