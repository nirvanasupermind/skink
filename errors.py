class Error(SystemExit):
    def __init__(self, msg):
        super().__init__(f'error: {msg}')