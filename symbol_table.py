class SymbolTable:
    def __init__(self, parent=None):
        self.keys = []
        self.values = []
        self.parent = parent
    
    def put(self, key, value):
        key = hash(key)
        if key in self.keys:
            self.values[self.keys.index(key)] = value
        else:
            self.keys.append(key)
            self.values.append(value)

    def get(self, key):
        key = hash(key)
        if key in self.keys:
            return self.values[self.keys.index(key)]
        else:
            if self.parent: return self.parent.get(key)
            return None