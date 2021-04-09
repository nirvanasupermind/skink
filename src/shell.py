#!/usr/bin/env python
import skink
import sys
# import os

# import only system from os


opts = skink.get(sys.argv,1)
fname = skink.get(sys.argv,2)
# f = open("/bin/foo.txt", "w")
# f.write("Testy Fox")

if opts == '-i':
    while True:
            text = input("skink> ")
            if text == '': continue
            if text == 'exit': break
            else:
                result, error = skink.run("<stdin>",text)
                if error: print(error.as_string())
                else: print(skink.prettyPrint(result))


# if opts == None and fname == None:
#     print("""Usage:
#              skink -i: Interactive shell
#              skink -f: Run file
#           """)