from tokens import Token, TokenType
from errors import Error
from nodes import Node

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.current_token = None
        self.advance()
    
    def raise_error(self, token):
        raise Error('invalid syntax', token.pos)

    def advance(self):
        token = self.current_token
        self.pos += 1
        try:
            self.current_token = self.tokens[self.pos]
        except IndexError:
            self.current_token = Token(TokenType.EOF, pos=token.pos if token else 0)

    def parse(self):
        if self.current_token.type == TokenType.EOF:
            return None
        
        result = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.raise_error(self.current_token)
        
        return result

    def expr(self):
        if self.current_token.matches(TokenType.KEYWORD, 'var'):
            self.advance()
            if self.current_token.type != TokenType.IDENTIFIER:
                self.raise_error()
                
            var_name_token = self.current_token
            self.advance()
            if self.current_token.type != TokenType.EQ:
                return Node(
                    ('var', var_name_token.value), 
                    var_name_token.pos
                )
                            
            self.advance()

            value = self.expr()
            self.advance()
            
            return Node(
                ('var', var_name_token.value, value), 
                var_name_token.pos
            )
        
        return self.assignment_expr()

    def assignment_expr(self):
        result = self.arith_expr()
        while self.current_token != None and self.current_token.type == TokenType.EQ:
            self.advance()
            result = Node(
                ('set', result, self.arith_expr()), 
                result.pos
            )

        return result 

    def arith_expr(self):
        result = self.term()
        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.advance()
                result = Node(
                    ('plus', result, self.term()), 
                    result.pos
                )
            elif self.current_token.type == TokenType.MINUS:
                self.advance()
                result = Node(
                    ('minus', result, self.term()),
                    result.pos
                )

        return result
    
    def term(self):
        result = self.factor()

        while self.current_token != None and self.current_token.type in (TokenType.MUL, TokenType.DIV):
            if self.current_token.type == TokenType.MUL:
                self.advance()
                result = Node(
                    ('mul', result, self.factor()),
                    self.pos
                )
            elif self.current_token.type == TokenType.DIV:
                self.advance()
                result = Node(
                    ('div', result, self.factor()),
                    self.pos
                )

        return result
    
    def factor(self):
        token = self.current_token

        if token.type == TokenType.LPAREN:
            self.advance()
            result = self.expr()
            
            if self.current_token.type != TokenType.RPAREN:
                self.raise_error(self.current_token)

            self.advance()
            
            return result
        elif token.type == TokenType.INT:
            self.advance()
            return Node(('int', token), token.pos)
        elif token.type == TokenType.FLOAT:
            self.advance()
            return Node(('float', token), token.pos)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return Node(('identifier', token), token.pos)
        elif token.type == TokenType.PLUS:
            self.advance()
            return Node(('uplus', self.factor()), token.pos)
        elif token.type == TokenType.MINUS:
            self.advance()
            return Node(('uminus', self.factor()), token.pos)
        else:
            self.raise_error(self.current_token)