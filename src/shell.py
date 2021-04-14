import skink
import sys
# import only system from os
from os import system, name
  
# import sleep to show output for some time period
from time import sleep
  
# define our clear function
def clear():
  
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


while True:
    text = input('skink> ')
    if text.strip() == "": continue
    if text == 'cls': clear();continue
    if text == 'exit': break
    result, error = skink.run('<stdin>', text)

    if error:
        print(error.as_string())
    else:
        # print(result)
        if len(result.get('elements')) == 1:
            print(skink.prettyPrint(result.get('elements')[0]))
        else:
            print(skink.prettyPrint(result))



