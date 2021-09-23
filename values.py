import numpy as np
from errors import Error

class Value: 
    def __init__(self):
        pass
    
    def add(self, file, line, other):
        self.illegal_operation(file, line)
    
    def subtract(self, file, line, other):
        self.illegal_operation(file, line)

    def multiply(self, file, line, other):
        self.illegal_operation(file, line)

    def divide(self, file, line, other):
        self.illegal_operation(file, line)
    
    def mod(self, file, line, other):
        self.illegal_operation(file, line)
    
    def plus(self, file, line):
        self.illegal_operation(file, line)
    
    def minus(self, file, line):
        self.illegal_operation(file, line)

    def illegal_operation(self, file, line):
        raise Error(file, line, 'illegal operation')

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def add(self, file, line, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        else:
            return self.illegal_operation(file, line)

    def subtract(self, file, line, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        else:
            return self.illegal_operation(file, line)
                
    def multiply(self, file, line, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        else:
            return self.illegal_operation(file, line)

    def divide(self, file, line, other):
        if isinstance(other, Number):
            if isinstance(other.value, int) and other.value == 0:
                raise Error(file, line, 'division by zero')         
            elif isinstance(other.value, float) and other.value == 0:
                return Number(np.inf)
            elif isinstance(self.value, float) or isinstance(other.value, float):
                return Number(self.value / other.value)
            else:
                return Number(self.value // other.value)
        else:
            return self.illegal_operation(file, line)  
             
    def mod(self, file, line, other):
        if isinstance(other, Number):
            if isinstance(other.value, int) and other.value == 0:
                raise Error(file, line, 'division by zero')         
            elif isinstance(other.value, float) and other.value == 0:
                return Number(np.nan)
            else:
                return Number(self.value % other.value)
        else:
            return self.illegal_operation(file, line)    
    
    def plus(self, file, line):
        return Number(+self.value)
    
    def minus(self, file, line):
        return Number(-self.value)

    def __repr__(self):
        return f'{self.value}'
    
class Nil(Value):
    def __init__(self):
        super().__init__()
    
    def __repr__(self):
        return 'nil'