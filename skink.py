from lexer import Lexer
# from parser_ import Parser

# def run_string(text):
#     run('<anonymous>', text)

def run(file):
    contents = open(file, 'r').read()
    
    _run(file.split('/')[-1], contents)
    
def _run(text):
    lexer = Lexer(text) 
    # tokens = lexer.generate_tokens()
    
    # # parser = Parser(file, tokens)

    # # print(f'tree: {parser.parse()}')