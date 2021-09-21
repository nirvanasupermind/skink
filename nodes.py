class Node:
    pass

class EmptyNode(Node):
    def __init__(self, line):
        self.line = line

    def __repr__(self):
        return f'(empty)'
    
class NumNode(Node):
    def __init__(self, line, token):
        self.line = line
        self.token = token

    def __repr__(self):
        return f'(num {self.token.value})'
    
class NilNode(Node):
    def __init__(self, line):
        self.line = line

    def __repr__(self):
        return f'(nil)'
    
class IdentifierNode(Node):
    def __init__(self, line, token):
        self.line = line
        self.token = token

    def __repr__(self):
        return f'(identifier {self.token.value})'
    
class BinaryNode(Node):
    def __init__(self, line, node_a, op, node_b):
        self.line = line
        self.node_a = node_a
        self.op = op
        self.node_b = node_b

    def __repr__(self):
        return f'({self.op.value} {self.node_a} {self.node_b})'
    
class UnaryNode(Node):
    def __init__(self, line, op, node_a):
        self.line = line
        self.op = op
        self.node_a = node_a

    def __repr__(self):
        return f'({self.op.value} {self.node_a})'

class VarNode(Node): 
    def __init__(self, line, name, value):
        self.line = line
        self.name = name
        self.value = value

    def __repr__(self):
        return f'(var {self.name} {self.value})'


class ProgramNode(Node):
    def __init__(self, line, statements):
        self.line = line
        self.statements = statements
    
    def __repr__(self):
        return f'(program {" ".join(map(str, self.statements))})'

