class Error(SystemExit):
    def __init__(self, file, line, msg):
        super().__init__(f'{file}:{line}: error: {msg}')