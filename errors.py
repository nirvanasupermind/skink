class Error(SystemExit):
    def __init__(self, message, pos=None):
        if pos:
            super().__init__(f'{pos.file}:{pos.line_and_column()}: error: {message}')
        else:
            super().__init__(f'error: {message}')