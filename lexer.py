import string
from errors import Error
from tokens import TokenType, Token

WHITESPACE = ' \t'
NEWLINES = ';\n'
LETTERS = '_' + string.ascii_letters
DIGITS = '0123456789'

class Lexer:
    def __init__(self, file, text):
        self.file = file
        self.text = iter(text)
        self.line = 1
        self.current_char = None
        self.keywords = [
            'var'
        ]

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
                tokens.append(self.get_newline())
            elif self.current_char == '.' or self.current_char in DIGITS:
                tokens.append(self.get_number())
            elif self.current_char in LETTERS:
                tokens.append(self.get_identifier())
            elif self.current_char == '`':
                tokens.append(self.get_backtick_identifier())
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
            elif self.current_char == '=':
                tokens.append(Token(self.line, TokenType.EQ))
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
    
    def get_newline(self):
        line = self.line

        newline_str = ''

        while self.current_char != None and self.current_char in NEWLINES:
            newline_str += self.current_char
            self.advance()
        
        return Token(line, TokenType.NEWLINE, newline_str)

    def get_number(self):
        line = self.line

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

        return Token(line, TokenType.NUMBER, number_str)  

    def get_identifier(self):
        line = self.line
        id_str = ''

        while self.current_char != None and self.current_char in (LETTERS + DIGITS):
            id_str += self.current_char
            self.advance()
        
        return Token(
            line, 
            TokenType.KEYWORD if id_str in self.keywords else TokenType.IDENTIIFIER, 
            id_str
        )
    

    def get_backtick_identifier(self):
        self.advance()
        
        line = self.line
        id_str = ''

        while self.current_char != '`':
            if self.current_char != '`':
                raise Error(self.file, self.line, 'unclosed backtick identifier')
            id_str += self.current_char
            self.advance()
    
                
        self.advance()

        return Token(
            line, 
            TokenType.IDENTIIFIER, 
            id_str
        )
    

    
        
    