from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter

def run_shell():
    while True:
        text = input('> ')
        if text == 'exit': break

        lexer = Lexer(text)
        tokens = lexer.generate_tokens()

        parser = Parser(tokens)
        tree = parser.parse()

        interpreter = Interpreter()
        print(interpreter.eval(tree))
    
run_shell()