from dataclasses import dataclass

class TokenType:
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MOD = 'MOD' 
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'

@dataclass
class Token:
    type: TokenType
    value: any = None

    def __repr__(self):
        return self.type + (f":{self.value}" if self.value != None else "")