from errors import Error
from tokens import Token, TokenType
from nodes import Node

class Parser:
    def __init__(self, file, tokens):
        self.file = file
        self.tokens = iter(tokens)
        self.advance()

    def raise_error(self, token):
        raise Error(self.file, token.line, 'syntax error')

    def advance(self):
        self.current_token = next(self.tokens)

    def parse(self):
        if self.current_token.type == TokenType.EOF:
            return Node(self.current_token.line, ('empty',))

        result = self.statements()

        if self.current_token.type != TokenType.EOF:
            self.raise_error(self.current_token)

        return result

    def statements(self):
        line = self.current_token.line
        statements = []

        statement = self.expr()
        statements.append(statement)

        while self.current_token != None and self.current_token.type == TokenType.NEWLINE:
            self.advance()
            statements.append(self.expr())
            
        return Node(line, ('statements', *statements))

    def expr(self):
        return self.additive_expr()
    
    def additive_expr(self):
        result = self.multiplicative_expr()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.advance()
                result = Node(result.line, ('add', result, self.multiplicative_expr()))
            elif self.current_token.type == TokenType.MINUS:
                self.advance()
                result = Node(result.line, ('subtract', result, self.multiplicative_expr()))

        return result

    def multiplicative_expr(self):
        result = self.factor()

        while self.current_token != None and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            if self.current_token.type == TokenType.MULTIPLY:
                self.advance()
                result = Node(result.line, ('multiply', result, self.factor()))
            elif self.current_token.type == TokenType.DIVIDE:
                self.advance()
                result = Node(result.line, ('divide', result, self.factor()))
            elif self.current_token.type == TokenType.MOD:
                self.advance()
                result = Node(result.line, ('mod', result, self.factor()))

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

        elif token.type == TokenType.NUMBER:
            self.advance()
            return Node(token.line, ('number', token.value))

        elif token.type == TokenType.PLUS:
            self.advance()
            return Node(token.line, ('plus', self.factor()))
        
        elif token.type == TokenType.MINUS:
            self.advance()
            return Node(token.line, ('minus', self.factor()))
        
        self.raise_error(self.current_token)