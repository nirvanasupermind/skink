from tokens import Token, TokenType
from errors import Error

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.advance()
    
    def raise_error(self):
        raise Error('invalid syntax')

    def advance(self):
        self.pos += 1
        try:
            self.current_token = self.tokens[self.pos]
        except IndexError:
            self.current_token = Token(TokenType.EOF)

    def parse(self):
        if self.current_token.type == TokenType.EOF:
            return None
        
        result = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.raise_error()
        
        return result
    
    def expr(self):
        result = self.term()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.advance()
                result = ('plus', result, self.term())
            elif self.current_token.type == TokenType.MINUS:
                self.advance()
                result = ('minus', result, self.term())

        return result
    
    def term(self):
        result = self.factor()

        while self.current_token != None and self.current_token.type in (TokenType.MUL, TokenType.DIV):
            if self.current_token.type == TokenType.MUL:
                self.advance()
                result = ('mul', result, self.factor())
            elif self.current_token.type == TokenType.DIV:
                self.advance()
                result = ('div', result, self.factor())

        return result
    
    def factor(self):
        token = self.current_token
        # print(token)

        if token.type == TokenType.LPAREN:
            self.advance()
            result = self.expr()
            
            if self.current_token.type != TokenType.RPAREN:
                self.raise_error()

            self.advance()
            
            return result
        elif token.type == TokenType.INT:
            self.advance()
            return ('int', token)
        elif token.type == TokenType.FLOAT:
            self.advance()
            return ('float', token)
        elif token.type == TokenType.PLUS:
            self.advance()
            return ('uplus', self.factor())
        elif token.type == TokenType.MINUS:
            self.advance()
            return ('uminus', self.factor())
        else:
            self.raise_error()