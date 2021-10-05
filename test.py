# from skink import run
from lexer import Lexer
from parser_ import Parser

text = '-5 + 2.2 * (4-1)'

lexer = Lexer(text)
tokens = lexer.generate_tokens()

parser = Parser(tokens)
tree = parser.parse()

print(tree)

# run('./test.skink')