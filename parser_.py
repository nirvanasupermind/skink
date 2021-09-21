from error import Error
from nodes import *

class Parser:
    def __init__(self, file, lexer):
        self.file = file
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    
    def error(self, token):
        if token.type == 'eof':
            raise Error(self.file, token.line, f'unexpected end of input')
        else:
            raise Error(self.file, token.line, f'unexpected "{token.value}"')

    def eat(self, type_):
        if self.current_token.type == type_:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(self.current_token) 

    def program(self):  
        if self.current_token.type == 'eof': # safety
            return ProgramNode(self.current_token.line, [])
        
        first_statement = self.expr()
        result = ProgramNode(first_statement.line, [first_statement])

        while self.current_token.type == 'newline':
            self.eat('newline')
            result.statements.append(self.expr())

        self.eat('eof')
        return result

    def expr(self):
        return self.add_expr()
    
    def add_expr(self):
        result = self.mul_expr()

        while self.current_token.type in '+-':
            op = self.current_token
            if self.current_token.type == '+':
                self.eat('+')
            elif self.current_token.type == '-':
                self.eat('-')
            else:
                self.error(self.current_token)

            result = BinaryNode(result.line, result, op, self.mul_expr())

        return result

    def mul_expr(self):
        result = self.unary_expr()

        while self.current_token.type in '*/%':
            op = self.current_token
            if op.type == '*':
                self.eat('*')
            elif op.type == '/':
                self.eat('/')
            elif op.type == '%':
                self.eat('%')
            else:
                self.error(self.current_token)

            result = BinaryNode(result.line, result, op, self.unary_expr())

        return result
    
    def unary_expr(self):
        op = self.current_token

        if op.type == '+':
            self.eat('+')
            return UnaryNode(op.line, op, self.unary_expr())
        elif op.type == '-':
            self.eat('-')
            return UnaryNode(op.line, op, self.unary_expr())
        else:
            return self.atom()
    
    def atom(self):
        token = self.current_token

        if token.type == 'num':
            self.eat('num')
            return NumNode(token.line, token)
        elif token.type == '(':
            self.eat('(')
            expr = self.expr()
            self.eat(')')

            return expr
        else:
            self.error(self.current_token)
            



