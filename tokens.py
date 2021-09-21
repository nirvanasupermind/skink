class Token:
    def __init__(self, line, type_, value):
        self.line = line
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f'({self.type}, {self.value})'