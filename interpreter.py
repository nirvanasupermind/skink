from values import *
from nodes import Node

class Interpreter:    
    def __init__(self, scope=None):
        if scope == None: scope = Interpreter.global_scope
        self.scope = scope

    def eval(self, node, scope):
        if node == None:
            return Null()
        if node.value[0] == 'int':
            return self.eval_int(node, scope)
        elif node.value[0] == 'float':
            return self.eval_float(node, scope)
        elif node.value[0] == 'identifier':
            return self.eval_identifier(node, scope)
        elif node.value[0] == 'plus':
            return self.eval_plus(node, scope)
        elif node.value[0] == 'minus':
            return self.eval_minus(node, scope)
        elif node.value[0] == 'mul':
            return self.eval_mul(node, scope)
        elif node.value[0] == 'div':
            return self.eval_div(node, scope)
        elif node.value[0] == 'uplus':
            return self.eval_uplus(node, scope)
        elif node.value[0] == 'uminus':
            return self.eval_uminus(node, scope)
        elif node.value[0] == 'var':
            return self.eval_var(node, scope)
        elif node.value[0] == 'set':
            return self.eval_set(node, scope)
        else:
            raise Exception('Unimplemented')

    def eval_int(self, node, scope):
        exp = node.value

        token = exp[1]
        tmp = np.clip(int(token.value), -2**63, 2**63-1) 
        return Int(np.int64(tmp)).set_pos(exp[1].pos)
    
    def eval_float(self, node, scope):
        exp = node.value

        token = exp[1]
        return Float(float(token.value)).set_pos(exp[1].pos)
    
    def eval_identifier(self, node, scope):
        exp = node.value

        name = exp[1].value
        result = scope.get(name)
        if result == None:
            raise Error(f'{name} is not defined', node.pos)

        return scope.get(name).set_pos(node.pos)

    def eval_plus(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)
        right = self.eval(exp[2], scope)

        return left + right

    def eval_minus(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)
        right = self.eval(exp[2], scope)
        
        return left - right
    
    def eval_mul(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)
        right = self.eval(exp[2], scope)
        
        return left * right

    def eval_div(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)
        right = self.eval(exp[2], scope)
        
        return left / right

    def eval_uplus(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)  
        return +left

    def eval_uminus(self, node, scope):
        exp = node.value

        left = self.eval(exp[1], scope)        
        return -left

    def eval_var(self, node, scope):
        exp = node.value

        name = exp[1]
        value = self.eval(exp[2], scope)
        if scope.get(name):
            raise Error(f'{name} is already defined', node.pos)

        scope.set(name, value)

        return value

    def eval_set(self, node, scope):
        exp = node.value
        tmp = exp[1]
        if tmp.value[0] != 'identifier':
            raise Error('invalid left-hand side in assignment', node.pos)

        name = tmp.value[1].value
        value = self.eval(exp[2], scope)
        if not scope.get(name):
            raise Error(f'{name} is not defined', node.pos)

        scope.set(name, value)

        return value

Interpreter.global_scope = Object()
Interpreter.global_scope.set('Object', Object.object_prototype)
Interpreter.global_scope.set('Int', Object.int_prototype)
Interpreter.global_scope.set('Float', Object.float_prototype)
Interpreter.global_scope.set('Null', Object.null_prototype)

Interpreter.global_scope.set('null', Null())