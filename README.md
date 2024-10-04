# TypeTamer 🔍


**Works on Python 3.10+**

TypeTamer catches 2 types of Anti-Patterns:

## 1. Multiple Constant Return Type 

Analyzer to catch functions with multiple return types

```
def sample_func(value):
    if value == 'Admin':
        return 1 
    return 'Access Denied'
```
### Why?

Since Python supports multiple return type, it is important to ensure that the function always return the same type of value hinted in type annotation. This is because the type of value returned by a function can affect the behavior of the program. 

### How it works?
![alt text](/assets/MultiReturnTypeChecker.png)

- MultiReturnTypeChecker will check the return type of the function and compare it with the type annotation.
- Currently only works for Union type, will add support for Optional type in the future.
- If function does not have type annotation, but it has multiple return statements with **different constant return types**, it will be reported as a violation. Else, if there are multiple return statements with same constant return type, it will be ignored.



### Cases that the checker will work 

1. Function with mismatch return type 
```
def test_with_mismatch_return()->int:
    return '2'

def test_with_union()->Union[int,bool]:
    if 1 > 0:
        return '2'
    return 2.0
```

2. Function with multiple return type 

```
def test_with_union_multiple_return(value)->Union[int,str]:
    if value == 'Admin':
        return True
    return 'Access Denied' 
```

### Cases that the checker will not work on

1. Function with multiple return type but are not constant(int, str, etc)
```
import random
def get_value():
    return random.choice([1, '2', 3.0])

def test_with_single_return(value):
    if value == 'Admin':
        return get_value() # I am not traversing Call Statements, so I won't 
    return 'Access Denied'
```



## 2. Mutable Default Args 

Analyzer to catch incorrect default arg, like using mutable instead of constant or none

```
def sample_func(value=[]):
    value.append(2)
    return 'True'

sample_func()
sample_func()
sample_func()

print(sample_func.__defaults__)
>>> ([2, 2, 2],)
```

### Why?

In Python, default arguments are stored at the time the function is defined, not when it’s called. When you define a function with default arguments, Python evaluates the default argument expressions and binds the resulting objects to the function’s bytecode object.

If the default argument is a mutable object like a list, dictionary, or set, it can lead to unexpected behavior because the same object is used for every call to the function.

### How it works?

![alt text](/assets/MutableDefaultArgsChecker.png)

- MutableDefaultArgChecker will check if the fucntion has default argument, if so, it will check if the default argument is a mutable object.
- If the default argument is a mutable object, it will be reported as a violation.

### Cases that the checker will work 

1. Function with mutable default arg

```
def test_with_mutable_literal(l=[], s={}):
    pass

def test_with_mutable_constructor(l=list(), s=set(), d=dict()):
    pass
```


## How to Run?

1. Setup python environment(Linux)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the checker on a file 

```
python main.py test.py

```
3. It will generate a report 'output.txt' in the same directory as the file you run the checker on.

![alt text](/assets/report.png)





## Results 


![alt text](/assets/results.png)


## Tests 

```
pytest unit_test.py

```
![alt text](/assets/test_results.png)



## To-Do 

- [] Add support for 3.x and 2.x 
- [] Handle cases with Optional generic  
- [] Handle return types with Call Statement 
- [] Report Formatting

I will first focus on adding support for 3.x. Along with adding support for Optional generic for MultiReturnTypeChecker. Also handle cases with Call Statement, which is complicated, as you might have a series of function call to get return value. 


