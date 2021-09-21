from error import Error
import numpy as np

class Value:
    def plus(self, file, line, other):
        self.illegal_operation(file, line)
        
    def minus(self, file, line, other):
        self.illegal_operation(file, line)

    def mul(self, file, line, other):
        self.illegal_operation(file, line)
      
    def div(self, file, line, other):
        self.illegal_operation(file, line)

    def pos(self, file, line):
        self.illegal_operation(file, line)

    def neg(self, file, line):
        self.illegal_operation(file, line)
    
    def illegal_operation(self, file, line):
        raise Error(file, line, 'illegal operation')

class Num(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def plus(self, file, line, other):
        if isinstance(other, Num):
            return Num(self.value + other.value)
        else:
            self.illegal_operation(file, line)
        
    def minus(self, file, line, other):
        if isinstance(other, Num):
            return Num(self.value - other.value)
        else:
            self.illegal_operation(file, line)
        
    def mul(self, file, line, other):
        if isinstance(other, Num):
            return Num(self.value * other.value)
        else:
            self.illegal_operation(file, line)
    
    def div(self, file, line, other):
        if isinstance(other, Num):
            if isinstance(other.value, float):
                try:
                    return Num(self.value / other.value)
                except ZeroDivisionError:
                    return Num(np.inf)
            elif other.value == 0:
                raise Error(file, line, 'attempt to divide by zero')
            else:
                return Num(self.value // other.value)
        else:
            self.illegal_operation(file, line)
        
    def mod(self, file, line, other):
        if isinstance(other, Num):
            if isinstance(other.value, float):
                try:
                    return Num(self.value % other.value)
                except ZeroDivisionError:
                    return Num(np.nan)
            elif other.value == 0:
                raise Error(file, line, 'attempt to divide by zero')
            else:
                return Num(self.value % other.value)
        else:
            self.illegal_operation(file, line)
        
    def pos(self, file, line):
        return Num(+self.value)

    def neg(self, file, line):
        return Num(-self.value)
    
    def __repr__(self):
        return str(self.value)
        
class Nil(Value):
    def __repr__(self):
        return 'nil'

        


