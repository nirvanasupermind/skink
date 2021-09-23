#!/usr/bin/env python
import sys
import skink

if len(sys.argv) == 1:
    while True:
        text = input('skink> ')
        if text == 'exit': break

        print(skink.run_string(text))
elif len(sys.argv) == 2:
    path = sys.argv[1]
    skink.run_file(path)
else:
    print('Usage: skink [ path ]')