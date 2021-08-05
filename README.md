# skink
**NOTICE**: implementation for this language is a work in progress

Skink is a small, dynamically-typed programming language. It emphasizes purely prototype-based code. 

```cpp
function fib(x) {
    if(x <= 1) {
        return 1;
    } else {
        return fib(x - 1) + fib(x - 2);
    }
}

System.print(fib(7)); //> 21
```
# Specification
See [SPEC.md](SPEC.md).

# Implementation
Skink's core is implemented in Python. The Skink evaluator executes a typed abstract syntax tree. 

# Use
In order to use this implementation of Skink, you must have the [python](https://www.python.org) and [pip](https://pypi.org/) installed.

