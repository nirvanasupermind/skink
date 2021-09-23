import sys
from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter

def _run(file, text):
    lexer = Lexer(file, text)
    tokens = lexer.get_tokens()

    parser = Parser(file, tokens)
    tree = parser.parse()

    interpreter = Interpreter(file)
    result = interpreter.visit(tree)

    print(result)

def run_string(source):
    _run('<anonymous>', source)

def run_file(path):
    _run(path.split('/')[-1], open(path, 'r').read())