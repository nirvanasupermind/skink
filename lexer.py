import string
from position import Position
from tokens import TokenType, Token
from errors import Error

WHITESPACE = ' \n\t'
LETTERS = string.ascii_letters + '$_'
DIGITS = '0123456789'
LETTERS_DIGITS = LETTERS + DIGITS

class Lexer:
    def __init__(self, text, file='<anonymous>'):
        self.text = text
        self.pos = Position(text, file, -1)
        self.advance()
    
    def advance(self):
        self.pos.advance()
        try:
            self.current_char = self.text[self.pos.idx]
        except IndexError:
            self.current_char = None

    def generate_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.advance()
            elif self.current_char in (DIGITS + '.'):
                tokens.append(self.generate_number())
            elif self.current_char in LETTERS:
                tokens.append(self.generate_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TokenType.PLUS, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.MUL, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIV, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, pos=self.pos.copy()))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TokenType.EQ, pos=self.pos.copy()))
                self.advance()
            else:
                raise Error(f'illegal character "{self.current_char}"', self.pos)
        
        return tokens


    def generate_number(self):
        decimal_point_count = 0
        number_str = self.current_char
        pos = self.pos.copy()

        self.advance()
        while self.current_char != None and (self.current_char in (DIGITS + '.')):
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    break

            number_str += self.current_char
            self.advance()
        
        if number_str.startswith('.'):
            number_str = '0' + number_str
            decimal_point_count += 1
        
        if number_str.endswith('.'):
            number_str += '0'
        
        if decimal_point_count == 0:
            return Token(TokenType.INT, number_str, pos)
        else:
            return Token(TokenType.FLOAT, number_str, pos)
        
    def generate_identifier(self):
        id_str = ''
        pos = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        tok_type = TokenType.KEYWORD if id_str in TokenType.KEYWORDS else TokenType.IDENTIFIER
        return Token(tok_type, id_str, pos)