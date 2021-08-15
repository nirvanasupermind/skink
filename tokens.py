class TokenType:
    INT = 'INT'
    FLOAT = 'FLOAT'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EQ = 'EQ'
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    EOF = 'EOF'
    KEYWORDS = [
        'var'
    ]

class Token:
    def __init__(self, type_, value=None, pos=None):
        self.type = type_
        self.value = value
        self.pos = pos
    
    def matches(self, type_, value):
        # print(type_, self.type)
        return self.type == type_ and self.value == value

    def __repr__(self):
        return self.type + (f':{self.value}' if self.value != None else '')