from lexer import Lexer

def run_shell():
    while True:
        text = input('> ')
        if text == 'exit': break

        lexer = Lexer(text)
        tokens = lexer.generate_tokens()
        print(tokens)
    
run_shell()