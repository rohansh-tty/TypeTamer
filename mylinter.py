from __future__ import annotations

import ast
import os
import sys
from typing import NamedTuple, Sequence

generic_primitive_types = {'int', 'float', 'str', 'bool'}

class Violation(NamedTuple):
    """
    Every rule violation contains a node that breaks the rule,
    and a message that will be shown to the user.
    """

    node: ast.AST
    message: str


class Checker(ast.NodeVisitor):
    """
    A Checker is a Visitor that defines a lint rule, and stores all the
    nodes that violate that lint rule.
    """

    def __init__(self, issue_code: str, description: str):
        self.issue_code = issue_code
        self.description = description
        self.violations: set[Violation] = set()


class Linter:
    """Holds all list rules, and runs them against a source file."""

    def __init__(self):
        self.checkers: set[Checker] = set()

    @staticmethod
    def print_violations(checker: Checker, file_name: str):
        """Prints all violations collected by a checker."""
        for node, message in checker.violations:
            print(
                f"{file_name}:{node.lineno}:{node.col_offset}:{node.name}:"
                f"[{checker.issue_code}] - {message}"
            )

    def run(self, source_path: str):
        """Runs all lints on a source file."""
        file_name = os.path.basename(source_path)

        with open(source_path) as source_file:
            source_code = source_file.read()
            
        with open('output.txt', 'w') as f:
            tree = ast.parse(source_code)
            for checker in self.checkers:
                f.write(f'checker name: {checker.__class__.__name__}\n')
                f.write(f'checker issue code: {checker.issue_code}\n')
                f.write(f'checker description: {checker.description}\n')
                checker.visit(tree)
                self.print_violations(checker, file_name)
                # write output to file
                for violation in checker.violations:
                    f.write(f"{violation.node.lineno}:{violation.node.col_offset}:{violation.message}\n")

class MutableDefaultArgsChecker(Checker):
    """
    Checker for default args, which ideally should be constant and not mutable 
    """
    def __init__(self, issue_code: str, description: str):
        super().__init__(issue_code, description)
        self.current_function: ast.FunctionDef | None = None 
        self.default_args = set()
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        super().generic_visit(node)
        if len(node.args.defaults):
            self.check_mutable_default_args(node)

    def check_mutable_default_args(self, node: ast.FunctionDef):
        for arg in node.args.defaults:
            if isinstance(arg, ast.Call):
                if arg.func.id in {'list', 'dict', 'set'}:
                    self.violations.add(Violation(node, f"Default argument is mutable, using None instead of {arg.func.id} as default"))
            if isinstance(arg, ast.List) or isinstance(arg, ast.Dict) or isinstance(arg, ast.Set):
                self.violations.add(Violation(node, f"Default argument is mutable, using None instead of {type(arg).__name__} as default"))


class MultiTypeConstantReturnChecker(Checker):
    """
    Checker for return types, which ideally should be constant and consistent 
    """
    def __init__(self, issue_code: str, description: str): 
        super().__init__(issue_code, description)
        self.return_types = set()
        self.current_function: ast.FunctionDef | None = None
        
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_function = node
        self.return_types.clear()
        super().generic_visit(node)
        
        if node.returns is None:
            if len(self.return_types) > 1:
                print(f'return types are {self.return_types}')
                self.violations.add(Violation(node, f"Multiple Return Types: {self.return_types!r}"))
                
        # handling single return type annotations
        elif isinstance(node.returns, ast.Name):
            # Works for 3.10+
            if isinstance(node.returns, ast.Name):
                if node.returns.id in generic_primitive_types:
                    for t in self.return_types:
                        if t != node.returns.id:
                            self.violations.add(Violation(node, f"Multiple Return Types: {self.return_types!r} with Type Annotations {node.returns.id}"))
                            
        # handling Union return type annotations
        elif isinstance(node.returns, ast.Subscript):
            if isinstance(node.returns.value, ast.Name):
                if node.returns.value.id == 'Union':
                    union_arg_types = [t.id for t in node.returns.slice.elts]
                    for t in self.return_types:
                        if t not in union_arg_types:
                            self.violations.add(Violation(node, f"Multiple Return Types: {self.return_types!r} with Union Type of {union_arg_types}"))
                
            
        
    def visit_Return(self, node: ast.Return):
        if self.current_function is None:
            return
        
        return_type = self.get_return_type(node.value)
        if return_type is not None:
            self.return_types.add(return_type)
    
    def get_return_type(self, node):
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        else:
            return None
      

checker_info = {
        "MutableDefaultArgsChecker": {
            "description": "When defining a function with default arguments, Python evaluates the default values immediately. If you use a mutable object (like a list or dictionary) as a default value, it can cause unexpected behavior because the same object is reused across function calls. To avoid this, use immutable objects or create a new mutable object in the function body.",
            "issue_code": "ML-100",
            "checker": MutableDefaultArgsChecker
        },
        "MultiTypeConstantReturnChecker": {
            "description": "Since Python supports multiple return type, it is important to ensure that the function always return the same type of value hinted in type annotation. This is because the type of value returned by a function can affect the behavior of the program.",
            "issue_code": "ML-200",
            "checker": MultiTypeConstantReturnChecker
        }
    }


if __name__ == "__main__":
    source_paths = sys.argv[1:]

    linter = Linter()
    
    for k,v in checker_info.items():
        issue_code = v["issue_code"]    
        description = v["description"]
        checker = v["checker"]
        linter.checkers.add(checker(issue_code=issue_code, description=description))
    
    

    for source_path in source_paths:
        linter.run(source_path)