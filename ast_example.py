import ast 


code = """
a = 10
c = 40
b = 100
if a > 100 and b < 100 and c == 200:
    print('this is ast here')
    
"""
code2 = """
a=0
b=9
c=8
if a > b > c:
    print('this wont work')
"""

code3 = """
name='rohan'
print(f'this is dumb print by {name}')"""

code4 = """
name='rohan'
print(f'this is dumb print by {name}')

for i in range(4):
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    


for i in range(10):
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    

"""

code5 = """
a="33"
b=50
c=909
print('a =',a)
print('b =',b)
print('c =',c)

"""


code6="""


def confusing(value):
    if value == 'Admin':
        a = 1
        return a
    return 'Access Denied'
"""

code6a = """
import random
def get_value()->int:
    return random.randint()
    
def sample():
    value = get_value()
    if value == 'Admin':
        return value
    return 'Access Denied' 

"""


code7 = """
import ast 
ast.parse("print('hello world')")
"""

class MyVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        # print(f'entering {node.__class__.__name__}')
        print(f'entering {ast.dump(node)}')
        super().generic_visit(node)
        print(f'leaving {ast.dump(node)}')

# counts statements under each for block
class ForStmtVisitor(ast.NodeVisitor):
    for_node = None 
    stmt_count = 0 
    
    def generic_visit(self, node):
        if self.for_node is not None:
            if isinstance(node, ast.stmt):
                self.stmt_count += 1
        elif self.for_node is None:
            if isinstance(node,ast.For):
                self.for_node = node 
                self.stmt_count = 0 
        
        super().generic_visit(node)
        
        if node is self.for_node:
            print(f'for loop has {self.stmt_count} statements')        
            self.for_node = None    
      
# number switch to convert all int/constants to a random number - this is creatign new node in ast, and those fixing is taken care by ast.fix_missing_locations
class NumberChanger(ast.NodeTransformer):
    def generic_visit(self, node):
        super().generic_visit(node)
        if not isinstance(node, ast.Constant) or not isinstance(node.value, int):    
            return node 
        return ast.Constant(value=93)      

# file writer, appending to existing Call node to write print statement to file instead
class FileWriter(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            node.keywords.append(
                ast.keyword(arg="file", value=ast.Name(id="myfile", ctx=ast.Load()))
            )      
        return node  

def get_ast(code):
    print(ast.dump(ast.parse(code), indent=4))
    
if __name__ == "__main__":
    v = MyVisitor()
    tree_dump = get_ast(code6a)
    # tree = ast.parse(code6)
    # v.visit(tree)
    # f = ForStmtVisitor()
    # f.visit(tree)
    # print(ast.dump(tree, indent=6))
    # modified_tree =ast.fix_missing_locations(NumberChanger().visit(tree))
    
    # exec(compile(tree, '', 'exec'))
    # exec(compile(modified_tree, '', 'exec'))