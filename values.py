class Value:
    def __add__(self, other):
        self.illegal_operation()
    
    def illegal_operation():
        raise Exception('illegal op')
    
    

class Num:
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return Num(self.value + other.value)
    
    
    