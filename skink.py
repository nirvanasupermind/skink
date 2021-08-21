from lexer import BasicLexer
from parser_ import BasicParser
from interpreter import BasicInterpreter

def run(filename):
    return runstring(open(filename, 'r').read())

def runstring(code):
    lexer = BasicLexer()
    parser = BasicParser()
    interpreter = BasicInterpreter()

    tokens = lexer.tokenize(code)
    ast = parser.parse(tokens)
    result = interpreter.walk(ast)

    return result
