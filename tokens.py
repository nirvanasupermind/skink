class Token:
    def __init__(self, line, type_, value):
        self.line = line
        self.type = type_
        self.value = value
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
        
    def __repr__(self):
        return f'({self.type}, {self.value})'