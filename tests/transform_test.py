from xert_transform import *
import inspect
import ast
import codegen

def f():
    global x
    if (x > 0):
        return
    x += 10

my_ast = ast.parse(inspect.getsource(f))
print codegen.to_source(my_ast)
new_ast = transform(my_ast)
print "---------------------"
print codegen.to_source(new_ast)
