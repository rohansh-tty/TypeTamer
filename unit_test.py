
## Unit Test by running ast 
import copy
import ast
from main import MutableDefaultArgsChecker, MultiTypeConstantReturnChecker, checker_info


#### MutableDefaultArgsChecker Tests ####
def test_with_mutable_literal_ast():
    source = """def test_with_mutable_literal(l=[], s={}):
        pass
    """
    tree = ast.parse(source)
    issue_code = checker_info["MutableDefaultArgsChecker"]["issue_code"]
    description = checker_info["MutableDefaultArgsChecker"]["description"]
    checker = MutableDefaultArgsChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    print('violations', checker.violations)
    assert len(checker.violations) == 2
    violation = next(iter(checker.violations))
    assert violation.node.lineno == 1
    assert violation.node.name == 'test_with_mutable_literal'
    assert violation.message.startswith('Default argument is mutable, using None instead of')
    
def test_with_mutable_constructor_ast():
    source = """def test_with_mutable_constructor(l=list(), s=set(), d=dict()):
        pass
    """
    tree = ast.parse(source)
    issue_code =   checker_info["MutableDefaultArgsChecker"]["issue_code"]
    description = checker_info["MutableDefaultArgsChecker"]["description"]
    checker = MutableDefaultArgsChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 3
    violation = next(iter(checker.violations))
    assert violation.node.lineno == 1
    assert violation.node.name == 'test_with_mutable_constructor'
    assert violation.message.startswith('Default argument is mutable, using None instead of')

def test_with_none_ast():
    source = """def test_with_none(l=None):
        pass
    """
    tree = ast.parse(source)
    issue_code = checker_info["MutableDefaultArgsChecker"]["issue_code"]
    description = checker_info["MutableDefaultArgsChecker"]["description"]
    checker = MutableDefaultArgsChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 0
    
### MultiTypeConstantReturnChecker Tests ###
def test_with_union():
    source = """def test_with_union()->Union[int,str]:
        if 1 > 0:
            return '2'
        return 2
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 0
    
def test_with_union2():
    source= """def test_with_union2()->Union[int,str]:
            return 2
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 0

def test_with_match_return():
    source = """def test_with_match_return()->int:
        return 2
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 0

def test_with_mismatch_return():
    source = """def test_with_mismatch_return()->int:
        return '2'
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 1
    violation = next(iter(checker.violations))
    assert violation.node.lineno == 1
    assert violation.node.name == 'test_with_mismatch_return'
    assert violation.message.startswith('Multiple Return Types:')
    
def test_with_union_single_return():
    source = """def test_with_union_single_return(value)->Union[int,str]:
        if value == 'Admin':
            return True
        return 'Access Denied' 
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    violation = next(iter(checker.violations))
    assert violation.node.lineno == 1
    assert violation.node.name == 'test_with_union_single_return'
    assert violation.message.startswith('Multiple Return Types:')
    
def test_with_union_multiple_return():
    source = """def test_with_union_multiple_return(value)->Union[int,str]:
        if value == 'Admin':
            return True
        return 'Access Denied' 
    """
    tree = ast.parse(source)
    issue_code = checker_info["MultiTypeConstantReturnChecker"]["issue_code"]
    description = checker_info["MultiTypeConstantReturnChecker"]["description"]
    checker = MultiTypeConstantReturnChecker(issue_code=issue_code, description=description)
    checker.visit(tree)
    assert len(checker.violations) == 1
    violation = next(iter(checker.violations))
    assert violation.node.lineno == 1
    assert violation.node.name == 'test_with_union_multiple_return'
    assert violation.message.startswith('Multiple Return Types:')   
    
