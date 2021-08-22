from sly import Lexer

class BasicLexer(Lexer):
    tokens = { INT, FLOAT }
    ignore = '\t '
    literals = { '+', '-', '*', '/', '%', '(', ')' }

    # INT = r'[0-9]+'
    # FLOAT = r'[0-9]+([.][0-9]*)'
    @_(r'([0-9]*\.[0-9]+|[0-9]+\.?)([Ee][+-]?[0-9]+)?')
    def NUMBER(self, t):
        if '.' in t.value:
            t.type = 'FLOAT'
        else:
            t.type = 'INT'
        
        return t

    # Newline token(used only for showing
    # errors in new line)
    @_(r'[\n\r;]+')
    def newline(self, t):
        self.lineno = t.value.count('\n')
        return t
  
    # tokens = { NAME, INT, FLOAT, STRING }
    # ignore = '\t '
    # literals = { '=', '+', '-', '/', 
    #             '*', '(', ')', ',', ';'}
  
    # # Define tokens as regular expressions
    # # (stored as raw strings)
    # NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    # STRING = r'\".*?\"'
  
    # # # Number token
    # # @_(r'\d+')
    # # def INT(self, t):
    # #     # convert it into a python integer
    # #     t.value = int(t.value) 
    # #     return t

    # # Float token
    # @_(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
    # def NUMBER(self, t):
    #     # convert it into a python float
    #     # print(t)
    #     # if '.' in t.value:
    #     #     t.type = 'FLOAT'
    #     # else:
    #     #     t.type = 'INT'
            
    #     # t.value = float(t.value) 

    #     return t

    # # # Float token
    # # @_(r'\d+([.]\d*)?)')
    # # def FLOAT(self, t):
    # #     # convert it into a python float
    # #     t.value = float(t.value) 
    # #     return t
    
    # # # Float token
    # # @_(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
    # # def FLOAT(self, t):
    # #     # convert it into a python float
    # #     t.value = float(t.value) 
    # #     return t
  
    # # Comment token
    # @_(r'//.*')
    # def COMMENT(self, t):
    #     pass
  
    # # Newline token(used only for showing
    # # errors in new line)
    # @_(r'\n+')
    # def newline(self, t):
    #     self.lineno = t.value.count('\n')