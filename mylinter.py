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
                f"{file_name}:{node.lineno}:{node.col_offset}: "
                f"{checker.issue_code}: {message}"
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
            



class MultiTypeReturnChecker(Checker):
    def __init__(self, issue_code: str): 
        super().__init__(issue_code)
        self.return_types = set()
        self.current_function: ast.FunctionDef | None = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # if Union return type, then we don't need to check
        if node.returns is None:
            self.current_function = node
            self.return_types.clear()
            super().generic_visit(node) 
            print(f'return types are {self.return_types}')
            if len(self.return_types) > 1:
                self.violations.add(Violation(node, f"Multiple Return Types: {self.return_types!r}"))
        
        
    def visit_Return(self, node: ast.Return):
        if self.current_function is None:
            return
        
        return_type = self.get_return_type(node.value)
        if return_type is not None:
            print(f'adding return type {return_type}')
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
            
        
    
if __name__ == "__main__":
    source_paths = sys.argv[1:]

    linter = Linter()
    linter.checkers.add(ConfusingTypeHintChecker(issue_code="W005"))
    
    # linter.checkers.add(MultiTypeReturnChecker(issue_code="W005"))

    for source_path in source_paths:
        linter.run(source_path)