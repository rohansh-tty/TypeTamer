from typing import Union


# MultiTypeConstantReturnChecker Tests
def test_with_union()->Union[int,str]:
    if 1 > 0:
        return '2'
    return 2

def test_with_union2()->Union[int,str]:
    return 2

def test_with_match_return()->int:
    return 2

def test_with_mismatch_return()->int:
    return '2'


def test_with_union_single_return(value)->Union[int,str]:
    if value == 'Admin':
        return True
    return 'Access Denied' 
    
def test_with_union_multiple_return(value)->Union[int,str]:
    if value == 'Admin':
        return True
    return 'Access Denied' 


# MutableDefaultArgsChecker Tests
def test_with_mutable_literal(l=[], s={}):
    pass

def test_with_mutable_constructor(l=list(), s=set(), d=dict()):
    pass

def test_with_none(l=None):
    pass 

def test_with_constant(l=1, d=list()):
    pass 

