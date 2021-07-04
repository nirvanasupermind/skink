import skink
while True:
    text = input('> ')

    if text == 'exit': break

    result, error = skink.runText('<stdin>', text)
    if(error): 
        print(error.as_string())
    else:
        print(result)