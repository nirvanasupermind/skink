import numpy as np
import uuid
from errors import Error

def to_int_or_float(value):
    return Int(value) if isinstance(value, np.int64) else Float(value)
    
class Object:
    def __init__(self, name='<anonymous>', prototype=None):
        self.keys = []
        self.values = []
        self.name = name
        self.prototype = prototype
        self.uuid = uuid.uuid4()
    
    def set(self, key, value):
        if key in self.keys:
            self.values[self.keys.index(key)] = value
        else:
            self.keys.append(key)
            self.values.append(value)

    def get(self, key):
        if key in self.keys:
            return self.values[self.keys.index(key)]
        else:
            if self.prototype:
                return self.prototype.get(key)
            else:
                return None
    
    def __add__(self, other):
        self.illegal_operation()

    def __sub__(self, other):
        self.illegal_operation()

    def __mul__(self, other):
        self.illegal_operation()

    def __truediv__(self, other):
        self.illegal_operation()

    def illegal_operation(self):
        raise Error('illegal operation')

class Int(Object):
    def __init__(self, value):
        super().__init__(prototype=Object.int_prototype)
        self.value = value

    def __add__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value + other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __sub__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value - other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __mul__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value * other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __truediv__(self, other):
        if isinstance(other, (Int, Float)):
            if isinstance(other, Int):
                result = self.value // other.value
            else:
                result = self.value / other.value

            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __repr__(self):
        return str(self.value)

class Float(Object):
    def __init__(self, value):
        super().__init__(prototype=Object.float_prototype)
        self.value = value
    
    def __add__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value + other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __sub__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value - other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __mul__(self, other):
        if isinstance(other, (Int, Float)):
            result = self.value * other.value
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __truediv__(self, other):
        if isinstance(other, (Int, Float)):
            try:
                result = self.value / other.value
            except ZeroDivisionError:
                return Float(np.inf)
            
            return to_int_or_float(result)
        else:
            self.illegal_operation()

    def __repr__(self):
        return str(self.value)
        
class Null(Object):
    def __init__(self):
        super().__init__(prototype=Object.null_prototype)

    def __repr__(self):
        return 'null'

Object.object_prototype = Object()
Object.int_prototype = Object(Object.object_prototype)
Object.float_prototype = Object(Object.object_prototype)
Object.null_prototype = Object(Object.object_prototype)