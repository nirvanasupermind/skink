class Node:
    pass

class NumNode(Node):
    def __init__(self, line, token):
        self.line = line
        self.token = token

    def __repr__(self):
        return f'(num {self.token.value})'
    
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
    
class ProgramNode(Node):
    def __init__(self, line, statements):
        self.line = line
        self.statements = statements
    
    def __repr__(self):
        return f'(program {" ".join(map(str, self.statements))})'

