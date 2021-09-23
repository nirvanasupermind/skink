from errors import Error
from tokens import TokenType, Token

WHITESPACE = ' \t'
NEWLINES = ';\n'
DIGITS = '0123456789'

class Lexer:
    def __init__(self, file, text):
        self.file = file
        self.text = iter(text)
        self.line = 1
        self.current_char = None

        self.advance()
    
    def advance(self):
        try:
            self.current_char = next(self.text)
        except StopIteration:
            self.current_char = None
        
        if self.current_char == '\n':
            self.line += 1
            
    def get_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.advance()
            elif self.current_char in NEWLINES:
                tokens.append(Token(self.line, TokenType.NEWLINE))
                self.advance()
            elif self.current_char == '.' or self.current_char in DIGITS:
                tokens.append(self.get_number())
            elif self.current_char == '+':
                tokens.append(Token(self.line, TokenType.PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(self.line, TokenType.MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(self.line, TokenType.MULTIPLY))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(self.line, TokenType.DIVIDE))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(self.line, TokenType.MOD))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(self.line, TokenType.LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(self.line, TokenType.RPAREN))
                self.advance()
            else:
                raise Error(self.file, self.line, 'lexical error')

        tokens.append(Token(self.line, TokenType.EOF))

        return tokens

    def get_number(self):
        decimal_point_count = 0
        number_str = self.current_char
        self.advance()

        while self.current_char != None and (self.current_char == '.' or self.current_char in DIGITS):
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    break
            
            number_str += self.current_char
            self.advance()

        if number_str.startswith('.'):
            number_str = '0' + number_str
        if number_str.endswith('.'):
            number_str += '0'

        return Token(self.line, TokenType.NUMBER, number_str)   