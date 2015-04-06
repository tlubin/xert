import ast
import inspect

class XertTransformer(ast.NodeTransformer):
    def __init__(self):
        self.globals = []
        self.passno = 0
        self.returnNode = None

    def visit_Global(self, node):
        self.globals.extend(node.names)
        return None
        
    def visit_Return(self, node):
        if self.passno == 0:
            return node
        else:
            return self.returnNode

def transform(func_ast):
    parser = XertTransformer()
    # First pass, remove all Global nodes ("global x,y") and collect the variables
    parser.visit(func_ast)
    parser.passno += 1

    # Add all written global variables as arguments
    assert len(func_ast.body[0].args.args) == 0, "TODO: right now functions can't take arguments"
    func_ast.body[0].args.args = map(lambda x: ast.Name(x, ast.Param()), parser.globals)

    # Construct return node as dictionary of written globals
    parser.returnNode = ast.Return(
        ast.Dict(map(lambda x: ast.Str(x), parser.globals), 
                 map(lambda x: ast.Name(x, ast.Load()), parser.globals))
    )

    # Add Return {'x': x, 'y': y, ...} at end if it doesn't exist
    if (not isinstance(func_ast.body[0].body[-1], ast.Return)):
        func_ast.body[0].body.append(parser.returnNode)

    # Second pass, change all Return nodes to return a dictionary of global variables
    parser.visit(func_ast)
    return func_ast
