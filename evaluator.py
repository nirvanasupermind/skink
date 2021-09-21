import numpy as np

from nodes import *
from values import *
from env import Env

class Evaluator:
    def __init__(self, file, env):
        self.file = file
        self.env = env

    def eval(self, node):
        if isinstance(node, EmptyNode):
            return Nil()
        elif isinstance(node, NumNode):
            if '.' in node.token.value:
                return Num(float(node.token.value))
            else:
                try:
                    return Num(np.int32(node.token.value))
                except OverflowError:
                    return Num(np.int32(int(node.token.value) % 2 ** 32))  
        elif isinstance(node, NilNode):
            return Nil()       
        elif isinstance(node, IdentifierNode):
            name = node.token.value

            if not self.env.contains(name):
                raise Error(self.file, node.line, f'{name} is not defined')
            
            return self.env.get(name)

        elif isinstance(node, BinaryNode):
            return self.eval_binary(node)
        elif isinstance(node, UnaryNode):
            return self.eval_unary(node)
        elif isinstance(node, VarNode):
            return self.eval_var(node)
        elif isinstance(node, ProgramNode):
            return self.eval_program(node)
        else:
            raise Exception(f'unknown node type: {type(node)}')

    def eval_binary(self, node):
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
        elif node.op.value == '=':
            if not isinstance(node.node_a, IdentifierNode):
                raise Error(self.file, node.line, 'invalid left-hand side in assignment')

            name = node.node_a.value
            if not self.env.contains(name):
                raise Error(self.file, node.line, f'{name} is not defined')
  
            self.env.set(name, arg2)
            return arg2
        else:
            return arg1.mod(self.file, node.node_a.line, arg2)

    def eval_unary(self, node):
        arg1 = self.eval(node.node_a)
            
        if node.op.value == '+':
            return arg1.pos(self.file, node.node_a.line)
        else:
            return arg1.neg(self.file, node.node_a.line)            

    def eval_var(self, node):
        name = node.name.value
        value = self.eval(node.value)

        if name in self.env.items:
            raise Error(self.file, node.line, f'{name} is already defined')

        self.env.set(name, value)
        return value

    def eval_program(self, node):
        accum = []

        for i in range(0, len(node.statements)):
            if isinstance(node.statements[i], EmptyNode): continue
            accum.append(self.eval(node.statements[i]))
            
        if(len(accum) == 0):
            return Nil()

        return accum[-1]
    
