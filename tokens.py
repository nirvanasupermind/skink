class TokenType:
    NEWLINE = 'NEWLINE'
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MOD = 'MOD'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'

class Token:
    def __init__(self, line, type_, value=None):
        self.line = line
        self.type = type_
        self.value = value
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
        
    def __repr__(self):
        return self.type + (f':{self.value}' if self.value is not None else '')