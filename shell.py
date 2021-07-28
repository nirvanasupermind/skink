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


while True:
    text = input('> ')
    if text == 'exit': 
        break
    else:
        result, error = skink.runstring(text)
        if error:
            print(error.as_string())
        else: 
            print(result)
