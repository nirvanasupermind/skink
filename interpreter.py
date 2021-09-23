import numpy as np  
from nodes import *
from values import *


class Interpreter:
    def __init__(self, file):
        self.file = file

    def clamp(self, a, b, c):
        return b if a < b else c if a > c else a

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node)
        
    def visit_EmptyNode(self, node):
        return Nil()

    def visit_NumberNode(self, node):
        if '.' in node.token.value:
            return Number(float(node.token.value))

        return Number(np.int64(np.clip(int(node.token.value), -9223372036854775808, 9223372036854775807)))

    def visit_AddNode(self, node):
        return self.visit(node.node_a).add(self.file, node.line, self.visit(node.node_b))

    def visit_SubtractNode(self, node):
        return self.visit(node.node_a).subtract(self.file, node.line, self.visit(node.node_b))

    def visit_MultiplyNode(self, node):
        return self.visit(node.node_a).multiply(self.file, node.line, self.visit(node.node_b))

    def visit_DivideNode(self, node):
        return self.visit(node.node_a).divide(self.file, node.line, self.visit(node.node_b))

    def visit_ModNode(self, node):
        return self.visit(node.node_a).mod(self.file, node.line, self.visit(node.node_b))

    def visit_PlusNode(self, node):
        return self.visit(node.node).plus(self.file, node.line)
    
    def visit_MinusNode(self, node):
        return self.visit(node.node).minus(self.file, node.line)
        
    def visit_StatementsNode(self, node):
        for i in range(0, len(node.statements) - 1):
             self.visit(node.statements[i])
            
        return self.visit(node.statements[-1])
