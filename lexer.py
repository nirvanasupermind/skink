from tokens import TokenType, Token

WHITESPACE = ' \n\t'
DIGITS = '0123456789'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.advance()
    
    def advance(self):
        self.pos += 1
        try:
            self.current_char = self.text[self.pos]
        except IndexError:
            self.current_char = None

    def generate_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.advance()
            elif self.current_char in (DIGITS + '.'):
                tokens.append(self.generate_number())
            elif self.current_char == '+':
                tokens.append(Token(TokenType.PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.MULTIPLY))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIVIDE))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN))
                self.advance()
            else:
                raise Exception(f'Illegal character "{self.current_char}"')
        
        return tokens


    def generate_number(self):
        decimal_point_count = 0
        number_str = self.current_char
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
        
        if number_str.endswith('.'):
            number_str += '0'
        
        if decimal_point_count == 0:
            return Token(TokenType.INT, int(number_str))
        else:
            return Token(TokenType.FLOAT, float(number_str))
    



