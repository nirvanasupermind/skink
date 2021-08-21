import uuid
import numpy as np
from symbol_table import SymbolTable
from errors import Error
import util

class Object:
    def __init__(self, proto=None):
        self.set_name()
        self.proto = proto
        self.uuid = uuid.uuid4()

        if self.proto:
            self.symbol_table = SymbolTable(self.proto.symbol_table)
        else:
            self.symbol_table = SymbolTable()
    
    def set_name(self, name='<anonymous>'):
        self.name = name
        return self

    def __add__(self, other):
        self.illegal_operation()
    
    def __sub__(self, other):
        self.illegal_operation()
    
    def __mul__(self, other):
        self.illegal_operation()

    def __truediv__(self, other):
        self.illegal_operation()

    def __mod__(self, other):
        self.illegal_operation()
    
    def __pos__(self):
        self.illegal_operation()
    
    def __neg_(self):
        self.illegal_operation()
    
    def __hash__(self):
        return hash(self.uuid)

    def illegal_operation(self):
        raise Error('illegal operation')

    def __repr__(self):
        return f'{(self.proto if self.proto else self).name}@{hex(hash(self))[2:]}'

Object.object_proto = Object().set_name('Object')
Object.int_proto = Object(Object.object_proto).set_name('Int')
Object.float_proto = Object(Object.object_proto).set_name('Float')
    
class Int(Object):
    def __init__(self, value):
        super().__init__(Object.int_proto)
        if isinstance(value, int): 
            value = np.clip(value, -9223372036854775808, 9223372036854775807)
        self.value = np.int64(value) 

    def __add__(self, other):
        result = self.value + other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __sub__(self, other):
        result = self.value - other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __mul__(self, other):
        result = self.value * other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)
    
    def __truediv__(self, other):
        if isinstance(other, Int):
            result = self.value // other.value
        else:
            result = self.value / other.value
            
        return Int(result) if isinstance(result, np.int64) else Float(result)
    
    def __mod__(self, other):
        result = self.value % other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __pos__(self):
        return Int(self.value)
    
    def __neg__(self):
        return Int(-self.value)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return str(self.value)
        
class Float(Object):
    def __init__(self, value):
        super().__init__(Object.float_proto)
        self.value = float(value)

    def __add__(self, other):
        result = self.value + other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __sub__(self, other):
        result = self.value - other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __mul__(self, other):
        result = self.value * other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)
    
    def __truediv__(self, other):
        try:
            result = self.value / other.value
        except ZeroDivisionError:
            result = np.inf
            
        return Int(result) if isinstance(result, np.int64) else Float(result)
    
    def __mod__(self, other):
        result = self.value % other.value
        return Int(result) if isinstance(result, np.int64) else Float(result)

    def __pos__(self):
        return Float(self.value)
    
    def __neg__(self):
        return Float(-self.value)

    def __hash__(self):
        return util.hash_float(self.value)
    
    def __repr__(self):
        return str(self.value)