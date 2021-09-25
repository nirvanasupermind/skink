from errors import Error
from tokens import Token, TokenType
from nodes import *

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
        result = self.statements()

        if self.current_token.type != TokenType.EOF:
            self.raise_error(self.current_token)

        return result

    def statements(self, stop_at=TokenType.EOF):
        if self.current_token.type == stop_at:
            return EmptyNode(self.current_token.line)
        
        statements = []
        line = self.current_token.line

        statement = self.expr()
        statements.append(statement)

        while self.current_token.type != TokenType.EOF and self.current_token.type == TokenType.NEWLINE:
            self.advance()

            statement = self.expr()
            statements.append(statement)       
        
        return StatementsNode(line, statements)     

    def expr(self):
        if self.current_token.matches(TokenType.KEYWORD, 'var'):
            return self.var_expr()
        else:
            return self.assignment_expr()

    def assignment_expr(self):
        result = self.additive_expr()

        while self.current_token.type != TokenType.EOF and self.current_token.type == TokenType.EQ:
            self.advance()
            result = AssignNode(result.line, result, self.term())

        return result

    def additive_expr(self):
        result = self.term()

        while self.current_token.type != TokenType.EOF and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.advance()
                result = AddNode(result.line, result, self.term())
            elif self.current_token.type == TokenType.MINUS:
                self.advance()
                result = SubtractNode(result.line, result, self.term())

        return result

    def var_expr(self):
        line = self.current_token.line
        self.advance()

        if self.current_token.type != TokenType.IDENTIIFIER:
            self.raise_error(self.current_token)
        
        name = self.current_token
        self.advance()

        if self.current_token.type != TokenType.EQ:
            self.raise_error(self.current_token)
    
        self.advance()
        value = self.expr()

        return VarNode(line, name, value)

    def term(self):
        result = self.factor()

        while self.current_token.type != TokenType.EOF and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            if self.current_token.type == TokenType.MULTIPLY:
                self.advance()
                result = MultiplyNode(result.line, result, self.factor())
            elif self.current_token.type == TokenType.DIVIDE:
                self.advance()
                result = DivideNode(result.line, result, self.factor())
            elif self.current_token.type == TokenType.MOD:
                self.advance()
                result = ModNode(result.line, result, self.factor())
                
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
            return NumberNode(token.line, token)

        elif token.type == TokenType.IDENTIIFIER:
            self.advance()
            return IdentifierNode(token.line, token)

        elif token.type == TokenType.PLUS:
            self.advance()
            factor = self.factor()
            return PlusNode(factor.line, factor)
        
        elif token.type == TokenType.MINUS:
            self.advance()
            factor = self.factor()
            return MinusNode(factor.line, factor)
        
        self.raise_error(self.current_token)