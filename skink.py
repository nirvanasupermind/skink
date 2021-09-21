from evaluator import Evaluator
from peekable_stream import PeekableStream
from lexer import Lexer
from parser_ import Parser

def _run(file, source):
    chars = PeekableStream(source)

    lexer = Lexer(file, chars)
    parser = Parser(file, lexer)
    tree = parser.program()

    evaluator = Evaluator(file)

    print(f'result:\n{evaluator.eval(tree)}')

def run_string(source):
    _run('<anonymous>', source)

def run_file(path):
    _run(path.split('/')[-1], open(path, 'r').read())