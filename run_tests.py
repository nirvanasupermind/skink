from io import StringIO
from subprocess import getoutput  # Python 3
import sys
import skink
import json

STARS = '** '

def getOutputFromFile(url):
    # Create the in-memory "file"
    temp_out = StringIO()

    # Replace default stdout (terminal) with our stream
    sys.stdout = temp_out

    skink.run(url)

    sys.stdout = sys.__stdout__

    result = temp_out.getvalue()
    return result

def join(arr):
    return ('\n').join(arr) + '\n'

expected_outputs = [
    ('./test/assignment/global.skink', join(['before', 'after', 'arg', 'arg'])),
    ('./test/assignment/infix_operator.skink', 'error'),
    ('./test/assignment/prefix_operator.skink', 'error'),
    ('./test/closure/closure_in_function.skink', join(['local'])),
    ('./test/closure/nested_closure.skink', join(['a', 'b', 'c'])),
    ('./test/comment/only_line_comment.skink', join([])),
    ('./test/comment/unicode.skink', join(['ok']))
]

def run_tests():
    failed_count = 0

    for el in expected_outputs:
        url, expected_output = el
        displayed = url.split('/')[-1]
        output = getOutputFromFile(url)
        if expected_output == 'error':
            if not ('Error' in output):
                failed_count += 1
                print(f'{STARS}test for {displayed} failed')
                print(f'expected output: {repr(expected_output)}')
                print(f'actual output: {repr(output)}')
            else:
                print(f'{STARS}test for {displayed} succeeded')
        else:
            if output != expected_output:
                failed_count += 1
                print(f'{STARS}test for {displayed} failed')
                print(f'\texpected output: {repr(expected_output)}')
                print(f'\tactual output: {repr(output)}')
            else:
                print(f'{STARS}test for {displayed} succeeded')

    
    print(f'{failed_count} tests failed')
run_tests()