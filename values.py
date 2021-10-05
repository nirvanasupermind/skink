import numpy as np
from dataclasses import dataclass

class Value:
    def illegal_operation(self):
        raise Exception('illegal operation')

@dataclass
class Number(Value):
    value: any

    def is_integer(self):
        return isinstance(self.value, np.int32)

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        else:
            self.illegal_operation()

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        else:
            self.illegal_operation()

    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        else:
            self.illegal_operation()

    def __truediv__(self, other):
        if isinstance(other, Number):
            if self.is_integer() and other.is_integer():
                return Number(self.value // other.value)
            else:
                return Number(self.value / other.value)
        else:
            self.illegal_operation()

    def __mod__(self, other):
        if isinstance(other, Number):
            return Number(self.value % other.value)
        else:
            self.illegal_operation()

    def __repr__(self):
        return f'{self.value}'