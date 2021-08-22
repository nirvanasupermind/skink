from sly import Parser
from lexer import BasicLexer

class BasicParser(Parser):
    #tokens are passed from lexer to parser
    tokens = BasicLexer.tokens
  
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/', '%')
    )

    def __init__(self):
        self.env = { }

    @_('expr')
    def statement(self, p):
        return p.expr
  
    @_('expr "+" expr')
    def expr(self, p):
        return ('plus', p.expr0, p.expr1)
  
    @_('expr "-" expr')
    def expr(self, p):
        return ('minus', p.expr0, p.expr1)
  
    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)
  
    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('expr "%" expr')
    def expr(self, p):
        return ('mod', p.expr0, p.expr1)
    
    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr
    
    @_('"+" expr')
    def expr(self, p):
        return ('uminus', p.expr)
    
    @_('"-" expr')
    def expr(self, p):
        return ('uminus', p.expr)
    
    @_('INT')
    def expr(self, p):
        return ('int', p.INT)
    
    @_('FLOAT')
    def expr(self, p):
        return ('float', p.FLOAT)