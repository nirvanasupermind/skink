from tokens import TokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.advance()

    def raise_error(self):
        raise Exception("Invalid syntax")

    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None

    def parse(self):
        if self.current_token == None:
            return None

        result = self.expr()

        if self.current_token != None:
            self.raise_error()

        return result

    def expr(self):
        result = self.term()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.advance()
                result = ('add', result, self.term())
            elif self.current_token.type == TokenType.MINUS:
                self.advance()
                result = ('subtract', result, self.term())

        return result

    def term(self):
        result = self.factor()

        while self.current_token != None and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            if self.current_token.type == TokenType.MULTIPLY:
                self.advance()
                result = ('multiply', result, self.factor())
            elif self.current_token.type == TokenType.DIVIDE:
                self.advance()
                result = ('divide', result, self.factor())
            elif self.current_token.type == TokenType.MOD:
                self.advance()
                result = ('mod', result, self.factor())
                
        return result

    def factor(self):
        token = self.current_token

        if token.type == TokenType.LPAREN:
            self.advance()
            result = self.expr()

            if self.current_token.type != TokenType.RPAREN:
                self.raise_error()
            
            self.advance()
            return result

        elif token.type == TokenType.NUMBER:
            self.advance()
            return ('number', token.value)

        elif token.type == TokenType.PLUS:
            self.advance()
            return ('plus', self.factor())
        
        elif token.type == TokenType.MINUS:
            self.advance()
            return ('minus', self.factor())
        
        self.raise_error()