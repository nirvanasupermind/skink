class EmptyNode:
    def __init__(self, line):
        self.line = line
    
    def  __repr__(self):
        return '(empty)'

class NumberNode:
    def __init__(self, line, token):
        self.line = line
        self.token = token
    
    def  __repr__(self):
        return f'(number {self.token.value})'

class IdentifierNode:
    def __init__(self, line, token):
        self.line = line
        self.token = token
    
    def  __repr__(self):
        return f'{self.token.value}'

class AddNode:
    def __init__(self, line, node_a, node_b):
        self.line = line
        self.node_a = node_a
        self.node_b = node_b
    
    def  __repr__(self):
        return f'(add {self.node_a} {self.node_b})'

class SubtractNode:
    def __init__(self, line, node_a, node_b):
        self.line = line
        self.node_a = node_a
        self.node_b = node_b
    
    def  __repr__(self):
        return f'(subtract {self.node_a} {self.node_b})'

class MultiplyNode:
    def __init__(self, line, node_a, node_b):
        self.line = line
        self.node_a = node_a
        self.node_b = node_b
    
    def  __repr__(self):
        return f'(multiply {self.node_a} {self.node_b})'

class DivideNode:
    def __init__(self, line, node_a, node_b):
        self.line = line
        self.node_a = node_a
        self.node_b = node_b
    
    def  __repr__(self):
        return f'(divide {self.node_a} {self.node_b})'

class ModNode:
    def __init__(self, line, node_a, node_b):
        self.line = line
        self.node_a = node_a
        self.node_b = node_b
    
    def  __repr__(self):
        return f'(mod {self.node_a} {self.node_b})'

class AssignNode:
    def __init__(self, line, name, value):
        self.line = line
        self.name = name
        self.value = value
    
    def  __repr__(self):
        return f'(assign {self.name} {self.value})'

class PlusNode:
    def __init__(self, line, node):
        self.line = line
        self.node = node
    
    def  __repr__(self):
        return f'(plus {self.node})'

class MinusNode:
    def __init__(self, line, node):
        self.line = line
        self.node = node
    
    def  __repr__(self):
        return f'(minus {self.node})'

class VarNode:
    def __init__(self, line, name, value):
        self.line = line
        self.name = name
        self.value = value
    
    def  __repr__(self):
        return f'(var {self.name.value} {self.value.value})'

class StatementsNode:
    def __init__(self, line, statements):
        self.line = line
        self.statements = statements
    
    def  __repr__(self):
        return f'(statements {" ".join(map(str, self.statements))})'
    