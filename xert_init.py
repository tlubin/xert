import ast
import inspect

class GlobalGetter(ast.NodeVisitor):
    def __init__(self):
        self.globs = set()

    def visit_Name(self, node):
        self.globs.add(node.id)

def get_globals(mod):
    t = ast.parse(inspect.getsource(mod))
    assert isinstance(t, ast.Module), 'Argument must be a module object'
    # scan the top level of the module for variable assignments
    getter = GlobalGetter()
    for node in t.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                getter.visit(target)
    return getter.globs

def get_initial_state(mod):
    return {g: mod.__dict__[g] for g in get_globals(mod)}
