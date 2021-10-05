from lexer import Lexer
from parser_ import Parser

def run(file):
    text = open(file, 'r').read()
    
    _run(text)

def _run(text):
    lexer = Lexer(text)
    tokens = lexer.generate_tokens()

    parser = Parser(tokens)
    tree = parser.parse()
    
    print(f'tree: {tree}')