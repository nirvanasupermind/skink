class Node:
    def __init__(self, line, sxp):
        self.line = line
        self.sxp = sxp
    
    def __repr__(self):
        return f'{self.sxp}'