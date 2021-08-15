class Error(SystemExit):
    def __init__(self, message):
        super().__init__(f'error: {message}')