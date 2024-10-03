Analyzer to catch multiple function with multiple return type 

```
def sample_func(value):
    if value == 'Admin':
        return 1 
    return 'Access Denied'
```

Analyzer to catch incorrect default arg, like using mutable instead of constant or none

```
def sample_func(value=[]):
    value.append(2)
    return 'True'
```
