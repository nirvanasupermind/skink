import skink
while True:
    text = input('> ')

    if text == 'exit': break

    result, error = skink.run_text('<stdin>', text)
    if(error): 
        print(error.as_string())
    else:
        print(result)