# Skink source code
# Usage permitted under terms of MIT License

#######################################
# IMPORTS
#######################################
import numpy as np

#######################################
# CONSTANTS
#######################################
DIGITS = '0123456789'


#######################################
# UTILITY FUNCTIONS
#######################################

#######################################
# ERRORS
#######################################
class LangError:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result

class IllegalCharError(LangError):
    def __init__(self, details):
        super().__init__('Illegal Character', details)



#######################################
# TOKENS
#######################################
TT_INT		= 'INT'
TT_LONG     = 'LONG'
TT_DOUBLE   = 'DOUBLE'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

#######################################
# LEXER
#######################################
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                # return some error
                char = self.current_char
                self.advance()
                return [], IllegalCharError(f'"{char}"')
        return tokens, []


    def make_number(self):
        num_str = ''
        l_count = 0
        dot_count = 0
        while self.current_char != None and self.current_char in (DIGITS + 'Ll.'):
            if self.current_char in 'Ll':
                if l_count == 1: break # there are no "long long"s yet
                l_count += 1
            elif self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        
        if dot_count == 1: # double
            return Token(TT_DOUBLE, float(num_str))
        elif l_count == 1: # long
            # todo: handle "Python int too large to convert to C long" here
            return Token(TT_LONG, np.int64(num_str))
        else: # int
            return Token(TT_INT, np.int32(num_str))
    


#######################################
# RUN
#######################################

def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error