from __future__ import annotations

import ast
import os
import sys
from typing import NamedTuple, Sequence


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

    def __init__(self, issue_code: str):
        self.issue_code = issue_code
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

        tree = ast.parse(source_code)
        print(f'tree is {ast.dump(tree,indent=4)}')
        for checker in self.checkers:
            checker.visit(tree)
            self.print_violations(checker, file_name)

# Checker for default args, which ideally should be constant and not mutable 
class MutableDefaultArgsChecker(Checker):
    def __init__(self, issue_code: str):
        super().__init__(issue_code)
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


class ConfusingTypeHintChecker(Checker):
    def __init__(self, issue_code: str):
        super().__init__(issue_code)
        self.current_function: ast.FunctionDef | None = None 
        self.return_types = set()
        self.type_hints = set()
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.returns is not None:
            self.type_hints.clear()
            self.return_types.clear()
            self.current_function = node
            super().generic_visit(node)
            self.type_hints.add(node.returns.id)
            if self.type_hints != self.return_types:
                self.violations.add(Violation(node, f"Confusing Type Hint: {self.type_hints}, while returning {self.return_types!r}"))

    def visit_Return(self, node: ast.Return):
        if self.current_function is None:
            return
        return_type = self.get_return_type(node.value)
        if return_type is not None:
            self.return_types.add(return_type)

    def get_return_type(self, node):
        if isinstance(node, ast.Call):
            return self.get_function_return_type(node.func.value)
        elif isinstance(node, ast.Constant):
            return type(node.value)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            # check fucntion type annotations 
            return self.get_return_type(node.id)
        else:
            return None
      
    def get_function_return_type(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in {'int', 'float', 'str', 'bool'}:
                return node.func.id
        return any
            


generic_primitive_types = {'int', 'float', 'str', 'bool'}
# handling only constant return types for now 
class MultiTypeConstantReturnChecker(Checker):
    def __init__(self, issue_code: str): 
        super().__init__(issue_code)
        self.return_types = set()
        self.current_function: ast.FunctionDef | None = None
        
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # TODO: if Union return type, then we don't need to check
        # TODO: if return type is primitive, and doesnt match the type of the return value, then we need to report it 
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
      
    def get_function_return_type(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in generic_primitive_types:
                return node.func.id
        return any
            
        

if __name__ == "__main__":
    source_paths = sys.argv[1:]

    linter = Linter()
    linter.checkers.add(MutableDefaultArgsChecker(issue_code="W001"))
    linter.checkers.add(MultiTypeConstantReturnChecker(issue_code="W002"))

    for source_path in source_paths:
        linter.run(source_path)