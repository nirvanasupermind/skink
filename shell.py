# Skink source code
# Usage permitted under terms of MIT License
#######################################
# IMPORTS
#######################################
import skink
try:
    import readline
except:
    pass #readline not available

print('Type "exit" to exit.')
while True:
    text = input('> ')

    if text == 'exit': break

    result, error = skink.run_text('<stdin>', text)
    if(error): 
        print(error.as_string())
    else:
        print(result)