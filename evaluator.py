import numpy as np

from nodes import *
from values import *

class Evaluator:
    def __init__(self, file):
        self.file = file

    def eval(self, node):
        if isinstance(node, NumNode):
            if '.' in node.token.value:
                return Num(float(node.token.value))
            else:
                try:
                    return Num(np.int32(node.token.value))
                except OverflowError:
                    return Num(np.int32(int(node.token.value) % 2 ** 32))
        elif isinstance(node, BinaryNode):
            arg1 = self.eval(node.node_a)
            arg2 = self.eval(node.node_b)

            if node.op.value == '+':
                return arg1.plus(self.file, node.node_a.line, arg2)
            elif node.op.value == '-':
                return arg1.minus(self.file, node.node_a.line, arg2)
            elif node.op.value == '*':
                return arg1.mul(self.file, node.node_a.line, arg2)
            elif node.op.value == '/':
                return arg1.div(self.file, node.node_a.line, arg2)
            else:
                return arg1.mod(self.file, node.node_a.line, arg2)
        elif isinstance(node, UnaryNode):
            arg1 = self.eval(node.node_a)
            
            if node.op.value == '+':
                return arg1.pos(self.file, node.node_a.line)
            else:
                return arg1.neg(self.file, node.node_a.line)
        elif isinstance(node, ProgramNode):
            if(len(node.statements) == 0):
                return Nil()

            for i in range(0, len(node.statements) - 1):
                self.eval(node.statements[i])
            
            return self.eval(node.statements[-1])
        else:
            raise Exception(f'unknown node {type(node)}')
            
    

    
    
