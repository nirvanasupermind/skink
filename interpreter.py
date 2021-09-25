import numpy as np  
from nodes import *
from values import *
from symbol_table import SymbolTable

class Interpreter:
    def __init__(self, file, global_symbol_table):
        self.file = file
        self.global_symbol_table = global_symbol_table

    def clamp(self, a, b, c):
        return b if a < b else c if a > c else a

    def visit(self, node, symbol_table):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node, symbol_table)
        
    def visit_VarAccessNode(self, node, symbol_table):
        name = node.token.value
        value = symbol_table.get(name)

        if not value:
            raise Error(self.file, node.line, f'"{name}" is not defined')

        return value

    def visit_EmptyNode(self, node, symbol_table):
        return Nil()

    def visit_NumberNode(self, node, symbol_table):
        if '.' in node.token.value:
            return Number(float(node.token.value))

        return Number(np.int64(np.clip(int(node.token.value), -9223372036854775808, 9223372036854775807)))

    def visit_IdentifierNode(self, node, symbol_table):
        name = node.token.value

        result = symbol_table.get(name)

        if result == None:
            raise Error(self.file, node.line, f'"{node.name} is not defined')

        return result

    def visit_AddNode(self, node, symbol_table):
        return self.visit(node.node_a, symbol_table).add(self.file, node.line, self.visit(node.node_b, symbol_table))

    def visit_SubtractNode(self, node, symbol_table):
        return self.visit(node.node_a, symbol_table).subtract(self.file, node.line, self.visit(node.node_b, symbol_table))

    def visit_MultiplyNode(self, node, symbol_table):
        return self.visit(node.node_a, symbol_table).multiply(self.file, node.line, self.visit(node.node_b, symbol_table))

    def visit_DivideNode(self, node, symbol_table):
        return self.visit(node.node_a, symbol_table).divide(self.file, node.line, self.visit(node.node_b, symbol_table))

    def visit_ModNode(self, node, symbol_table):
        return self.visit(node.node_a, symbol_table).mod(self.file, node.line, self.visit(node.node_b, symbol_table))

    def visit_AssignNode(self, node, symbol_table):        
        if not isinstance(node.name, IdentifierNode):
            raise Error(self.file, node.line, 'illegal assignment')

        name = node.name.token.value
        value = self.visit(node.value, symbol_table)

        if symbol_table.get(name) == None:
            raise Error(self.file, node.line, f'"{name}" is not defined')
        
        symbol_table.set(name, value)
        return value

    def visit_PlusNode(self, node, symbol_table):
        return self.visit(node.node, symbol_table).plus(self.file, node.line)
    
    def visit_MinusNode(self, node, symbol_table):
        return self.visit(node.node, symbol_table).minus(self.file, node.line)
    
    def visit_VarNode(self, node, symbol_table):
        name = node.name.value
        value = self.visit(node.value, symbol_table)

        if name in symbol_table.symbols:
            raise Error(self.file, node.line, f'"{name}" is already defined')

        symbol_table.set(name, value)
        return value

    def visit_StatementsNode(self, node, symbol_table):
        for i in range(0, len(node.statements) - 1):
             self.visit(node.statements[i], symbol_table)
            
        return self.visit(node.statements[-1], symbol_table)
