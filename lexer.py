import re
from error import Error
from tokens import Token

DIGITS = '0123456789'

class Lexer:
    def __init__(self, file, chars):
        self.file = file
        self.line = 1
        self.chars = chars
        self.keywords = [
            'var'
        ]

    def _scan(self, first_char, allowed):
        result = first_char
        p = self.chars.next

        while p is not None and re.match(allowed, p):
            result += self.chars.move_next()
            p = self.chars.next

        return result
        
    
    def _scan_string(self, delim, desc):
        result = delim
        while self.chars.next != delim:
            c = self.chars.move_next()
            if c == '\n': self.line += 1

            if c is None:
                raise Error(self.file, self.line, f'unclosed {desc}')
            result += c

        self.chars.move_next()
        result += delim

        return result

    def _scan_num(self, first_char):
        result = first_char
        p = self.chars.next
        decimal_points = 0

        while p is not None and re.match('[.0-9]', p):
            if p == '.':
                if decimal_points >= 1: break
                decimal_points += 1

            result += self.chars.move_next()
            p = self.chars.next

        return result

    
    def get_next_token(self):
        c = self.chars.move_next() 
        if c == None:
            return Token(self.line, 'eof', '')
        elif c in ' \t':             
            return self.get_next_token()
        elif c in ';\n':
            result = Token(self.line, 'newline', c)
            if c == '\n': self.line += 1
            return result
        elif c in '+-*/%=()':
            return Token(self.line, c, c) 
        elif re.match('[.0-9]', c):
            value = self._scan_num(c)
            return Token(self.line, 'num', value)
        elif re.match('[_a-zA-Z0-9]+', c):
            identifier = self._scan(c, '[_a-zA-Z0-9]+')

            if identifier in self.keywords:
                return Token(self.line, 'keyword', identifier)
            else:
                return Token(self.line, 'identifier', identifier)
        elif c == '`':
            value = self._scan_string('`', 'backtick identifier')
            return Token(self.line, 'identifier', value)
        else:
            raise Error(self.file, self.line, f'unexpected "{c}"')