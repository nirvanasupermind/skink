import re

class Position:
    def __init__(self, text, file, idx):
        self.text = text
        self.file = file
        self.idx = idx
    
    def advance(self):
        self.idx += 1

    def line_number(self):
        tempString = self.text[0:self.idx]
        return len(re.split('\n|\r', tempString))

    def line_and_column(self):
        tempString = self.text[0:self.idx]
        line = len(re.split('\n|\r', tempString))
        column = len(re.split('\n|\r', tempString)[-1]) + 1

        return f'{line}:{column}'

    def copy(self):
        return Position(self.text, self.file, self.idx)
    