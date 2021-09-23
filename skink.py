import sys
from lexer import Lexer

def _run(file, text):
    lexer = Lexer(file, text)

    print(f'tokens:\n{lexer.get_tokens()}')

def run_string(source):
    _run('<anonymous>', source)

def run_file(path):
    _run(path.split('/')[-1], open(path, 'r').read())