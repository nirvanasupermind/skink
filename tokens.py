class TokenType:
    EOF = 'EOF'
    NEWLINE = 'NEWLINE'
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MOD = 'MOD'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'

class Token:
    def __init__(self, line, type_, value=None):
        self.line = line
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f'{self.type}{":" + self.value if self.value != None else ""}'