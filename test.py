
# from lexer import BasicLexer
# from parser_ import BasicParser
# from interpreter import BasicInterpreter

import skink

print(skink.runstring('1 + 2 * -3'))

# tokens = BasicLexer().tokenize('10.5')
# i = -1

# while True:
#     i += 1
#     try:
#         print(f'i={i}, {next(tokens)}')
#     except StopIteration:
#         break


# print(BasicParser().parse(BasicLexer().tokenize('10 + 5')))
