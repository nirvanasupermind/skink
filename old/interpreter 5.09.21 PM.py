from values import *

class BasicInterpreter:
    def walk(self, node):
        if node[0] == 'int':
            return self.walk_int(node)
        elif node[0] == 'float':
            return self.walk_float(node)
        elif node[0] == 'plus':
            return self.walk_plus(node)
        elif node[0] == 'minus':
            return self.walk_minus(node)
        elif node[0] == 'mul':
            return self.walk_mul(node)
        elif node[0] == 'div':
            return self.walk_div(node)
        elif node[0] == 'mod':
            return self.walk_mod(node)
        elif node[0] == 'uplus':
            return self.walk_uplus(node)
        elif node[0] == 'uminus':
            return self.walk_uminus(node)
        else:
            raise Exception('Unimplemented')

    def walk_int(self, node):
        return Int(int(node[1]))

    def walk_float(self, node):
        return Float(node[1])
    
    def walk_plus(self, node):
        return self.walk(node[1]) + self.walk(node[2])

    def walk_minus(self, node):
        return self.walk(node[1]) - self.walk(node[2])

    def walk_mul(self, node):
        return self.walk(node[1]) * self.walk(node[2])

    def walk_div(self, node):
        return self.walk(node[1]) / self.walk(node[2])

    def walk_mod(self, node):
        return self.walk(node[1]) % self.walk(node[2])

    def walk_uplus(self, node):
        return +self.walk(node[1])

    def walk_uminus(self, node):
        return -self.walk(node[1])

